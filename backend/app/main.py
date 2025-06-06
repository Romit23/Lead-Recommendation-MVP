from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
from app.lead_scorer import score_leads
from app.hunter_verifier import verify_email
import os
import uuid
import csv
from typing import List, Dict, Any
from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from typing import Optional

app = FastAPI()

# Load sample data
df = pd.read_csv('data/leads.csv')
df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]

class Lead(BaseModel):
    id: str
    name: str
    email: str
    company: str
    job_title: str
    website: str
    location: str
    industry: str
    score: float
    verified: bool = False

class Feedback(BaseModel):
    lead_id: str
    converted: bool

# In-memory storage for simplicity
leads_data = []
feedback_data = []

@app.on_event("startup")
async def startup_event():
    global leads_data
    # Initial scoring
    leads_data = score_leads(df.to_dict('records'))
    # Initial verification for first 10 leads
    for lead in leads_data[:10]:
        lead['verified'] = verify_email(lead['email'])

@app.get("/leads", response_model=List[Lead])
async def get_leads(limit: int = 100):
    sorted_leads = sorted(leads_data, key=lambda x: x['score'], reverse=True)
    return sorted_leads[:limit]

@app.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    lead = next((l for l in leads_data if l['id'] == lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Real-time verification
    if not lead.get('verified'):
        lead['verified'] = verify_email(lead['email'])
    
    return lead

@app.post("/feedback/")
async def submit_feedback(feedback: Feedback):
    feedback_data.append({
        'lead_id': feedback.lead_id,
        'converted': feedback.converted,
        'timestamp': pd.Timestamp.now()
    })
    return {"message": "Feedback received"}

@app.get("/export/")
async def export_leads():
    # Update verification status before export
    for lead in leads_data:
        if not lead.get('verified'):
            lead['verified'] = verify_email(lead['email'])
    
    # Create CSV
    filename = "verified_leads.csv"
    keys = leads_data[0].keys() if leads_data else []
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(leads_data)
    
    return FileResponse(filename, media_type='text/csv', filename=filename)

# Add to your imports
from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
import os
from pydantic import BaseModel

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

@app.post("/send-email")
async def send_email(email: EmailRequest, background_tasks: BackgroundTasks):
    """Endpoint to handle email sending"""
    background_tasks.add_task(
        send_email_sync,
        email.to,
        email.subject,
        email.body
    )
    return {"status": "queued"}

def send_email_sync(to_email: str, subject: str, body: str):
    """Synchronous email sending function"""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv("SMTP_FROM", "noreply@example.com")
        msg['To'] = to_email
        
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT", 587))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email failed to {to_email}: {str(e)}")
        return False