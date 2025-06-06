import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from typing import List, Dict, Any

# Mock model for MVP (would use real data in production)
def score_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    df = pd.DataFrame(leads)
    
    # Mock scoring criteria
    features = pd.DataFrame({
        'job_title_rank': df['job_title'].apply(lambda x: len(x.split()) if isinstance(x, str) else 1),
        'domain_power': df['website'].apply(lambda x: 1 if x and '.com' in x else 0),
        'location_score': df['location'].apply(lambda x: 0.8 if 'New York' in x else 0.5),
        'email_length': df['email'].apply(lambda x: len(x) if isinstance(x, str) else 10)
    })
    
    # Mock model training (in real app, use historical conversion data)
    X = features.fillna(0)
    y = np.random.randint(0, 2, len(X))  # Mock labels
    
    model = RandomForestClassifier()
    model.fit(X, y)
    
    # Predict scores
    df['score'] = model.predict_proba(X)[:, 1]
    df['score'] = df['score'].round(2) * 100  
    
    # Apply feedback adjustments
    if hasattr(score_leads, 'feedback_weights'):
        for idx, row in df.iterrows():
            if row['id'] in score_leads.feedback_weights:
                df.at[idx, 'score'] *= score_leads.feedback_weights[row['id']]
    
    return df.to_dict('records')

# Initialize feedback weights
score_leads.feedback_weights = {}

def update_model_with_feedback(feedback_data):
    """Update model based on feedback (simplified)"""
    for feedback in feedback_data:
        lead_id = feedback['lead_id']
        converted = feedback['converted']
        
        # Adjust weight based on feedback
        if converted:
            score_leads.feedback_weights[lead_id] = 1.2  # Increase score
        else:
            score_leads.feedback_weights[lead_id] = 0.8  # Decrease score