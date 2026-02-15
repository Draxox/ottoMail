import sqlite3

def reset_all():
    conn = sqlite3.connect("copilot.db")
    c = conn.cursor()
    c.execute("DELETE FROM clients")
    c.execute("DELETE FROM proposals")
    conn.commit()
    print("Database cleared.")
    conn.close()

if __name__ == "__main__":
    reset_all()
