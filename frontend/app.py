import streamlit as st
import requests
import pandas as pd
import time

# Config
BACKEND_URL = "http://backend:8000"
st.set_page_config(layout="wide")

# Session state
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'selected_lead' not in st.session_state:
    st.session_state.selected_lead = None

def load_leads():
    response = requests.get(f"{BACKEND_URL}/leads?limit=100")
    if response.status_code == 200:
        st.session_state.leads = response.json()

def submit_feedback(lead_id, converted):
    requests.post(
        f"{BACKEND_URL}/feedback/",
        json={"lead_id": lead_id, "converted": converted}
    )
    st.success("Feedback submitted!")

# Main UI
st.title("AI-Powered Lead Recommendation System")

# Lead list
st.header("Top Scoring Leads")
if st.button("Refresh Leads"):
    load_leads()

if not st.session_state.leads:
    load_leads()

df = pd.DataFrame(st.session_state.leads)

# Industry filter
industries = sorted(df["industry"].dropna().unique())
selected_industries = st.multiselect("Filter by Industry", industries, default=industries)
df = df[df["industry"].isin(selected_industries)]

# Table view
view_df = df[['name', 'email', 'company', 'industry', 'score', 'verified']].copy()
view_df['Select'] = False
edited_df = st.data_editor(
    view_df,
    column_config={
        "Select": st.column_config.CheckboxColumn(required=True),
        "score": st.column_config.ProgressColumn(
            format="%d%%", min_value=0, max_value=100
        ),
        "verified": st.column_config.CheckboxColumn()
    },
    hide_index=True,
    disabled=["name", "email", "company", "industry", "score", "verified"]
)

# Lead details
selected_rows = edited_df[edited_df.Select]
if not selected_rows.empty:
    lead_email = selected_rows.iloc[0].email
    st.session_state.selected_lead = next(
        (l for l in st.session_state.leads if l['email'] == lead_email), 
        None
    )

if st.session_state.selected_lead:
    with st.expander("Lead Details", expanded=True):
        lead = st.session_state.selected_lead
        st.subheader(lead['name'])
        cols = st.columns(3)
        cols[0].metric("Score", f"{lead['score']}%")
        cols[1].metric("Verification", "Verified" if lead['verified'] else "Pending")
        cols[2].metric("Company", lead['company'])

        st.write(f"**Email:** {lead['email']}")
        st.write(f"**Job Title:** {lead['job_title']}")
        st.write(f"**Location:** {lead['location']}")
        st.write(f"**Website:** {lead['website']}")
        st.write(f"**Industry:** {lead['industry']}")

        # Feedback
        st.subheader("Feedback")
        if st.button("Mark as Converted", key="converted"):
            submit_feedback(lead['id'], True)
        if st.button("Mark as Not Converted", key="not_converted"):
            submit_feedback(lead['id'], False)

# Export
st.divider()
st.header("Export Leads")

# Export selected leads
if not selected_rows.empty:
    export_df = df[df['email'].isin(selected_rows.email)]
    st.download_button(
        label="Download Selected Leads as CSV",
        data=export_df.to_csv(index=False),
        file_name="selected_leads.csv",
        mime="text/csv"
    )

# Export all verified leads
if st.button("Export Verified Leads to CSV"):
    with st.spinner("Exporting..."):
        response = requests.get(f"{BACKEND_URL}/export/")
        if response.status_code == 200:
            st.download_button(
                label="Download CSV",
                data=response.content,
                file_name="verified_leads.csv",
                mime="text/csv"
            )

# Automated Outreach
st.divider()
st.header("Automated Outreach")
email_template = st.text_area(
    "Email Template",
    value="""Subject: Partnership Opportunity with {company}

Hi {name},

I noticed your work at {company} and thought our solution might help you achieve {goal}. 

Would you be open to a quick chat next week?

Best,
Your Sales Team
"""
)


def send_single_email(lead, subject, body):
    """Helper function to send individual email"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/send-email",
            json={
                "to": lead['email'],
                "subject": subject,
                "body": body
            },
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error sending to {lead['email']}: {str(e)}")
        return False

if st.button("Schedule Outreach"):
    # Get ONLY selected leads
    selected_indices = edited_df[edited_df['Select']].index.tolist()
    selected_leads = [l for i, l in enumerate(st.session_state.leads) if i in selected_indices]
    
    if not selected_leads:
        st.error("Please select at least one lead by checking the boxes")
    else:
        # Prepare email template
        template_lines = email_template.split('\n')
        subject = template_lines[0].replace('Subject:', '').strip()
        body_template = '\n'.join(template_lines[1:])
        
        success_count = 0
        failed_emails = []
        
        for lead in selected_leads:
            # Format email body with lead data
            body = body_template.format(
                company=lead.get('company', ''),
                name=lead.get('name', ''),
                goal="your business goals"
            )
            
            if send_single_email(lead, subject, body):
                success_count += 1
            else:
                failed_emails.append(lead['email'])
        
        # Show results
        st.success(f"Successfully scheduled {success_count} emails")
        if failed_emails:
            st.error(f"Failed to send to: {', '.join(failed_emails)}")
        
        # Debug output (visible only in development)
        st.json({
            "selected_leads": [l['email'] for l in selected_leads],
            "total_selected": len(selected_leads),
            "template_used": email_template
        })
