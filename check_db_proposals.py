import sqlite3
from app.models import Proposal, Client

conn = sqlite3.connect("copilot.db")
c = conn.cursor()

print("CLIENTS:")
c.execute("SELECT * FROM clients")
print(c.fetchall())

print("\nPROPOSALS:")
c.execute("SELECT * FROM proposals")
print(c.fetchall())

conn.close()
