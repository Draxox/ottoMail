"""Gmail MCP integration"""
import os
import base64
import pickle
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailMCP:
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        creds_file = "credentials.json"
        token_file = "token.json"
        
        creds = None
        if os.path.exists(token_file):
            with open(token_file, 'rb') as f:
                creds = pickle.load(f)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_file, 'wb') as f:
                pickle.dump(creds, f)
        
        return build('gmail', 'v1', credentials=creds)
    
    async def get_unread_emails(self, max_results=5):
        results = self.service.users().messages().list(
            userId='me',
            q='is:unread in:inbox',
            maxResults=max_results
        ).execute()
        
        emails = []
        for msg in results.get('messages', []):
            email = self._get_email_details(msg['id'])
            emails.append(email)
        return emails
    
    def _get_email_details(self, msg_id):
        msg = self.service.users().messages().get(
            userId='me', id=msg_id, format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        body = self._extract_body(msg['payload'])
        
        return {
            'id': msg_id,
            'from': headers.get('From', ''),
            'subject': headers.get('Subject', ''),
            'body': body,
            'thread_id': msg['threadId']
        }
    
    def _extract_body(self, payload):
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        return ""
    
    async def create_draft(self, to, subject, body, thread_id=None):
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft_body = {'message': {'raw': raw}}
        if thread_id:
            draft_body['message']['threadId'] = thread_id
        
        draft = self.service.users().drafts().create(
            userId='me', body=draft_body
        ).execute()
        return draft['id']
    
    async def send_draft(self, draft_id):
        self.service.users().drafts().send(userId='me', body={'id': draft_id}).execute()
    
    async def mark_as_read(self, msg_id):
        self.service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
