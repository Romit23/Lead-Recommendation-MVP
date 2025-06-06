import requests
import os
import time

def verify_email(email: str) -> bool:
    """Verify email using Hunter.io API with caching"""
    # Mock verification for development
    if os.getenv("ENVIRONMENT") == "development":
        return len(email.split("@")) == 2
    
    # Real verification with Hunter.io
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key:
        raise ValueError("Hunter API key not configured")
    
    try:
        response = requests.get(
            f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={api_key}"
        )
        data = response.json()
        return data.get('data', {}).get('status') == 'valid'
    except Exception:
        return False