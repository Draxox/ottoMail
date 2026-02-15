import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

print(f"Connecting to {EMAIL_USER}...")
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL_USER, EMAIL_PASSWORD)
mail.select("INBOX")

status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()[-3:]

print(f"Found {len(email_ids)} emails.")
for email_id in email_ids:
    res, msg = mail.fetch(email_id, "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            print(f"Subject: {subject}")
