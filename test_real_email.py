"""Test agent with REAL emails from Gmail inbox"""
import asyncio
import json
import imaplib
import email
from email.header import decode_header
from agent.graph import EmailAgentGraph
from integrations.llm_wrapper import UnifiedLLM
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")


def get_gmail_emails(max_emails=3):
    """Fetch emails from Gmail inbox"""
    print("=" * 80)
    print(f"CONNECTING TO GMAIL: {EMAIL_USER}")
    print("=" * 80)
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        print(f"[OK] Connected to Gmail\n")
        
        mail.select("INBOX")
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()[-max_emails:]  # Get last N emails
        
        emails = []
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            
            # Get sender
            sender = msg.get("From", "Unknown")
            
            # Get body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            
            emails.append({
                "id": email_id.decode(),
                "from": sender,
                "subject": subject,
                "body": body[:1000]  # Take first 1000 chars
            })
        
        mail.close()
        mail.logout()
        return emails
        
    except Exception as e:
        print(f"[ERROR] Error connecting to Gmail: {e}")
        print(f"\nMake sure:")
        print(f"  1. EMAIL_USER = {EMAIL_USER}")
        print(f"  2. EMAIL_PASSWORD is correct (16-char app password)")
        print(f"  3. Gmail IMAP is enabled (Settings > Forwarding and POP/IMAP)")
        print(f"\nTo get app password:")
        print(f"  https://myaccount.google.com → Security → App passwords")
        return []


async def test_real_emails():
    """Test agent with real Gmail emails"""
    
    print(f"\nLLM Provider: {LLM_PROVIDER.upper()}")
    print("=" * 80)
    
    # Get real emails
    emails = get_gmail_emails(max_emails=2)
    
    if not emails:
        print("\n[ERROR] No emails found. Exiting.")
        return
    
    print(f"[OK] Found {len(emails)} email(s) to process\n")
    
    # Create LLM and graph
    llm = UnifiedLLM()
    graph = EmailAgentGraph(llm)
    
    # Process each email
    for idx, gmail_email in enumerate(emails, 1):
        print("\n" + "=" * 80)
        print(f"EMAIL #{idx}")
        print("=" * 80)
        print(f"From: {gmail_email['from']}")
        print(f"Subject: {gmail_email['subject']}")
        print(f"Body preview: {gmail_email['body'][:150]}...\n")
        
        initial_state = {
            "messages": [],
            "email_id": gmail_email["id"],
            "email_from": gmail_email["from"],
            "email_subject": gmail_email["subject"],
            "email_body": gmail_email["body"],
            "thread_id": gmail_email["id"],
            "client_name": None,
            "company": None,
            "project_type": None,
            "requirements": None,
            "timeline": None,
            "budget": None,
            "project_plan": None,
            "cost_estimate": None,
            "proposal_text": None,
            "is_valid_inquiry": False,
            "confidence_score": 0.0,
            "needs_human_review": False,
            "current_step": "starting",
            "error": None
        }
        
        print("Processing with AI...\n")
        result = await graph.graph.ainvoke(initial_state)
        
        # Save result for verification
        with open("last_run_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        
        # Display results
        print("=" * 80)
        print("CLASSIFICATION")
        print("=" * 80)
        print(f"Valid: {result.get('is_valid_inquiry')}")
        conf = result.get('confidence_score', 0)
        if isinstance(conf, (int, float)):
            print(f"Confidence: {conf:.0%}" if conf <= 1 else f"Confidence: {conf}%")
        status = result.get('current_step', '?')
        print(f"Status: {status}\n")
        
        if not result.get('is_valid_inquiry'):
            print("(Skipping - not a valid inquiry)\n")
            continue
        
        print("=" * 80)
        print("EXTRACTED DATA")
        print("=" * 80)
        print(f"Client: {result.get('client_name', 'N/A')}")
        print(f"Company: {result.get('company', 'N/A')}")
        print(f"Project: {result.get('project_type', 'N/A')}")
        print(f"Timeline: {result.get('timeline', 'N/A')}")
        print(f"Budget: {result.get('budget', 'N/A')}\n")
        
        reqs = result.get('requirements')
        if reqs and isinstance(reqs, list):
            print("Requirements:")
            for req in reqs:
                print(f"  • {req}")
        
        print("\n" + "=" * 80)
        print("PROJECT PLAN")
        print("=" * 80)
        plan = result.get('project_plan', {})
        if plan:
            print(f"Complexity: {plan.get('complexity', 'N/A')}")
            print(f"Hours: {plan.get('total_estimated_hours', 'N/A')}")
            print(f"Phases: {len(plan.get('phases', []))}")
        
        print("\n" + "=" * 80)
        print("COST")
        print("=" * 80)
        cost = result.get('cost_estimate', {})
        if cost:
            print(f"Min: ${cost.get('min', 'N/A'):,}" if isinstance(cost.get('min'), int) else f"Min: {cost.get('min', 'N/A')}")
            print(f"Max: ${cost.get('max', 'N/A'):,}" if isinstance(cost.get('max'), int) else f"Max: {cost.get('max', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("GENERATED PROPOSAL")
        print("=" * 80)
        proposal = result.get('proposal_text', '')
        if proposal:
            # Show first 500 chars
            if len(proposal) > 500:
                print(proposal[:500] + f"\n\n[... {len(proposal)-500} more characters ...]")
            else:
                print(proposal)
        else:
            print("(No proposal generated)")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    if not EMAIL_PASSWORD or EMAIL_PASSWORD == "xxxx xxxx xxxx xxxx":
        print("=" * 80)
        print("ERROR: Gmail app password not set!")
        print("=" * 80)
        print("\nYou need to:")
        print("1. Go to: https://myaccount.google.com/security")
        print("2. Find 'App passwords'")
        print("3. Generate password for Mail + Windows")
        print("4. Copy the 16-character password")
        print("5. Paste it in .env as: EMAIL_PASSWORD=xxxx xxxx xxxx xxxx")
        print("\nThen run this script again.")
        exit(1)
    
    asyncio.run(test_real_emails())
