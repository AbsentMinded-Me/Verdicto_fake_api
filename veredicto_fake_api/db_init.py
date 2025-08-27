import sqlite3

con = sqlite3.connect("verdicto.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS legal_units (
    id INTEGER PRIMARY KEY,
    act TEXT,
    section TEXT,
    title TEXT NOT NULL,
    state TEXT,
    citation TEXT,
    summary TEXT,
    tags TEXT,
    risk_level TEXT,
    metadata_json TEXT
);
""")

con.commit()
con.close()
print("Database initialized ✅")
