"""Standard IMAP/SMTP Email Service"""
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.header import decode_header
from pydantic_settings import BaseSettings

class EmailConfig(BaseSettings):
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    IMAP_SERVER: str = "imap.gmail.com"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465

    class Config:
        env_file = ".env"
        extra = "ignore"

config = EmailConfig()

class StandardEmailService:
    def __init__(self):
        self.imap_server = config.IMAP_SERVER
        self.smtp_server = config.SMTP_SERVER
        self.user = config.EMAIL_USER
        self.password = config.EMAIL_PASSWORD

    def _connect_imap(self):
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.user, self.password)
        return mail

    async def get_unread_emails(self, max_results=5):
        """Fetch unread emails from Inbox"""
        # Note: In a real async app, this should run in a thread executor
        # but for simplicity in MVP we'll run blocking or wrap in asyncio.to_thread
        import asyncio
        return await asyncio.to_thread(self._fetch_emails_blocking, max_results)

    def _fetch_emails_blocking(self, max_results):
        mail = self._connect_imap()
        try:
            mail.select("inbox")
            # Fetch ALL messages (to catch ones user might have opened)
            # We rely on DB deduping to avoid re-processing
            status, messages = mail.search(None, "ALL")
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            # Get latest 5 emails
            email_ids = email_ids[-max_results:]
            print(f"[DEBUG] Fetching emails: {email_ids}")
            
            results = []
            for e_id in email_ids:
                print(f"[DEBUG] Fetching email ID: {e_id}")
                _, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        from_ = msg.get("From")
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        body = part.get_payload(decode=True).decode(errors='replace')
                                    except:
                                        body = part.get_payload(decode=True).decode('latin-1', errors='replace')
                                    break
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode(errors='replace')
                            except:
                                body = msg.get_payload(decode=True).decode('latin-1', errors='replace')

                        results.append({
                            "id": e_id.decode(),
                            "from": from_,
                            "subject": subject,
                            "body": body,
                            "thread_id": e_id.decode() # IMAP doesn't have native thread_id same as Gmail API
                        })
            return results
        finally:
            mail.logout()

    async def create_draft(self, to, subject, body, thread_id=None):
        """Simulate draft creation by returning a placeholder ID."""
        return "LOCAL_DRAFT_ID"

    async def send_email(self, to, subject, body):
        """Send the email using SMTP"""
        import asyncio
        await asyncio.to_thread(self._send_email_blocking, to, subject, body)

    def _send_email_blocking(self, to, subject, body):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.user
        msg["To"] = to

        with smtplib.SMTP_SSL(self.smtp_server, config.SMTP_PORT) as server:
            server.login(self.user, self.password)
            server.send_message(msg)

    async def mark_as_read(self, msg_id):
        """Mark email as seen"""
        import asyncio
        await asyncio.to_thread(self._mark_read_blocking, msg_id)

    def _mark_read_blocking(self, msg_id):
        mail = self._connect_imap()
        try:
            mail.select("inbox")
            mail.store(msg_id, "+FLAGS", "\\Seen")
        finally:
            mail.logout()
