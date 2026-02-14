from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import pickle
import os

class GmailMCP:
    """
    MCP-compliant Gmail integration
    Provides standardized interface for agent
    """
    
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        """OAuth2 authentication"""
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                ['https://www.googleapis.com/auth/gmail.modify']
            )
            creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)
    
    async def get_unread_emails(self, max_results: int = 10) -> List[Dict]:
        """MCP Tool: Fetch unread emails"""
        
        results = self.service.users().messages().list(
            userId='me',
            q='is:unread in:inbox',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            email = self._get_email_details(msg['id'])
            emails.append(email)
        
        return emails
    
    def _get_email_details(self, message_id: str) -> Dict:
        """Extract full email data"""
        msg = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        
        return {
            'id': message_id,
            'thread_id': msg['threadId'],
            'from': headers.get('From', ''),
            'subject': headers.get('Subject', ''),
            'body': self._extract_body(msg['payload']),
            'date': headers.get('Date', '')
        }
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from complex MIME structure"""
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        
        return ""
    
    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None
    ) -> str:
        """MCP Tool: Create email draft"""
        
        from email.mime.text import MIMEText
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        draft_body = {'message': {'raw': raw}}
        if thread_id:
            draft_body['message']['threadId'] = thread_id
        
        draft = self.service.users().drafts().create(
            userId='me',
            body=draft_body
        ).execute()
        
        return draft['id']
    
    async def mark_as_read(self, message_id: str) -> bool:
        """MCP Tool: Mark email as processed"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking as read: {e}")
            return False
