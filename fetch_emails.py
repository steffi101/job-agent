# fetch_emails.py - Fetch job alert emails from Gmail

import base64
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from auth import get_gmail_service
from config import JOB_ALERT_SENDERS, EMAIL_LOOKBACK_DAYS


def get_job_alert_emails(days_back=EMAIL_LOOKBACK_DAYS):
    """
    Fetch job alert emails from the last N days.
    """
    service = get_gmail_service()
    
    # Build search query for job alerts
    sender_query = ' OR '.join([f'from:{sender}' for sender in JOB_ALERT_SENDERS])
    
    # Also search by subject keywords as backup
    subject_query = '(subject:job subject:alert) OR (subject:jobs subject:you) OR (subject:"new job") OR (subject:careers)'
    
    # Date filter
    after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    date_query = f'after:{after_date}'
    
    # Combined query
    query = f'({sender_query} OR {subject_query}) {date_query}'
    
    print(f"Searching emails...")
    
    # Fetch message IDs
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=100
    ).execute()
    
    messages = results.get('messages', [])
    print(f"Found {len(messages)} potential job alert emails")
    
    emails = []
    for msg in messages:
        email_data = get_email_content(service, msg['id'])
        if email_data:
            emails.append(email_data)
    
    return emails


def get_email_content(service, msg_id):
    """Get full content of a single email."""
    try:
        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        headers = {h['name'].lower(): h['value'] for h in message['payload']['headers']}
        
        subject = headers.get('subject', '')
        sender = headers.get('from', '')
        date_str = headers.get('date', '')
        
        try:
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.now()
        
        body = extract_body(message['payload'])
        links = extract_links(body)
        
        return {
            'id': msg_id,
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'links': links
        }
    
    except Exception as e:
        print(f"Error fetching email {msg_id}: {e}")
        return None


def extract_body(payload):
    """Extract text body from email payload"""
    body = ''
    
    if 'body' in payload and payload['body'].get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    
    elif 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif part['mimeType'] == 'text/html':
                if 'data' in part['body']:
                    html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    body += html  # Keep HTML for link extraction
            elif 'parts' in part:
                body += extract_body(part)
    
    return body


def extract_links(text):
    """Extract URLs from text"""
    # Get ALL http/https links
    url_pattern = r'https?://[^\s<>"\']+[^\s<>"\'\.,;:\)]'
    links = re.findall(url_pattern, text, re.IGNORECASE)
    
    # Deduplicate while preserving order
    seen = set()
    unique_links = []
    for link in links:
        link = link.rstrip('.,;:')
        if link not in seen:
            seen.add(link)
            unique_links.append(link)
    
    return unique_links


if __name__ == '__main__':
    emails = get_job_alert_emails(days_back=7)
    for email in emails:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['sender']}")
        print(f"Links: {len(email['links'])}")
        print("---")
