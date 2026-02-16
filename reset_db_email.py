import sqlite3

def reset_email(email_id):
    conn = sqlite3.connect("copilot.db")
    c = conn.cursor()
    c.execute("DELETE FROM processed_emails WHERE email_id = ?", (email_id,))
    c.execute("DELETE FROM proposals WHERE id IN (SELECT id FROM proposals WHERE client_id IN (SELECT id FROM clients WHERE email LIKE '%krish.learndev%'))") 
    # That might be too complex, just clearing processed_emails is enough to trigger the agent logic again.
    # The agent might create duplicate client/proposal entries but that's fine for a demo.
    conn.commit()
    print(f"Reset email {email_id}")
    conn.close()

if __name__ == "__main__":
    reset_email("12874")
