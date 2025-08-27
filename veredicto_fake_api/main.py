import sqlite3
import json
import pickle
from fastapi import FastAPI, Depends, HTTPException

# ---------------------- Load Trained Models ----------------------
with open("risk_model.pkl", "rb") as f:
    risk_model = pickle.load(f)

with open("risk_vectorizer.pkl", "rb") as f:
    risk_vectorizer = pickle.load(f)

with open("summary_model.pkl", "rb") as f:
    summary_model = pickle.load(f)

with open("summary_vectorizer.pkl", "rb") as f:
    summary_vectorizer = pickle.load(f)

# Example summaries (replace with your dataset summaries)
summaries = [
    "Whoever fails to comply with the provisions shall be punishable with imprisonment up to 5 years or fine up to Rs. 1 lakh."
]

# ---------------------- FastAPI App ----------------------
app = FastAPI(title="Verdicto API")

# ---------------------- DB Dependency ----------------------
def get_db():
    con = sqlite3.connect("verdicto.db")
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()

# ---------------------- Health Check ----------------------
@app.get("/health")
def health():
    return {"ok": True}

# ---------------------- List Laws ----------------------
@app.get("/laws")
def list_laws(
    state: str | None = None,
    act: str | None = None,
    risk_level: str | None = None,
    tag: str | None = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    List all laws with optional filters:
    - state
    - act
    - risk_level (High/Medium/Low)
    - tag (matches CSV tags field)
    """
    query = "SELECT * FROM legal_documents WHERE 1=1"
    params = []

    if state:
        query += " AND state = ?"
        params.append(state)

    if act:
        query += " AND act = ?"
        params.append(act)

    if risk_level:
        query += " AND risk_level = ?"
        params.append(risk_level)

    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")

    rows = db.execute(query, params).fetchall()

    # Convert rows -> dict and parse metadata_json
    results = []
    for r in rows:
        d = dict(r)
        if d.get("metadata_json"):
            d["metadata"] = json.loads(d["metadata_json"])
        results.append(d)

    return results

# ---------------------- Get Single Law ----------------------
@app.get("/laws/{law_id}")
def get_law(law_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Fetch a single law by ID
    """
    row = db.execute("SELECT * FROM legal_documents WHERE id = ?", (law_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Law not found")

    d = dict(row)
    if d.get("metadata_json"):
        d["metadata"] = json.loads(d["metadata_json"])
    return d

# ---------------------- Analyze Document ----------------------
@app.post("/analyze")
def analyze_document(document: str):
    """
    Input: raw legal text
    Output: summary + risk analysis
    """
    response = {}

    # ----- Risk Analysis -----
    risk_vec = risk_vectorizer.transform([document])
    predicted_risk = risk_model.predict(risk_vec)[0]
    response["risks"] = [{"clause": document, "risk_level": predicted_risk}]

    # ----- Summary Retrieval -----
    doc_vec = summary_vectorizer.transform([document])
    _, indices = summary_model.kneighbors(doc_vec, n_neighbors=1)
    closest_summary = summaries[indices[0][0]]
    response["summary"] = closest_summary

    return response
