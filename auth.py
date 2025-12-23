# auth.py - Gmail API Authentication

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope - read only
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service(credentials_path='credentials.json', token_path='token.pickle'):
    """
    Authenticate with Gmail API and return service object.
    
    First run will open browser for OAuth consent.
    Subsequent runs will use saved token.
    """
    creds = None
    
    # Load existing token if available
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future runs
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    # Build and return Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service


def test_connection():
    """Test Gmail API connection"""
    try:
        service = get_gmail_service()
        # Try to get user profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Connected to Gmail as: {profile['emailAddress']}")
        print(f"   Total messages: {profile['messagesTotal']}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == '__main__':
    test_connection()
