import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
import pickle

# -------- Load Dataset --------
with open("fake_legal_data.json", "r") as f:
    data = json.load(f)

# Flatten risks into a clause-level dataset
risk_rows = []
for entry in data:
    for risk in entry["risks"]:
        risk_rows.append({
            "summary": entry["summary"],
            "clause": risk["clause"],
            "risk_level": risk["risk_level"]
        })

df_risks = pd.DataFrame(risk_rows)

# -------- Risk Classification Model --------
X_risk = df_risks["clause"]
y_risk = df_risks["risk_level"]

risk_vectorizer = TfidfVectorizer()
X_risk_vec = risk_vectorizer.fit_transform(X_risk)

risk_model = LogisticRegression(max_iter=1000)
risk_model.fit(X_risk_vec, y_risk)

# -------- Summary Retrieval Model --------
# We'll use Nearest Neighbors on summaries for quick matching
summaries = [entry["summary"] for entry in data]
summary_vectorizer = TfidfVectorizer()
X_summary_vec = summary_vectorizer.fit_transform(summaries)

summary_model = NearestNeighbors(n_neighbors=1, metric="cosine")
summary_model.fit(X_summary_vec)

# -------- Save Models --------
with open("risk_model.pkl", "wb") as f:
    pickle.dump(risk_model, f)

with open("risk_vectorizer.pkl", "wb") as f:
    pickle.dump(risk_vectorizer, f)

with open("summary_model.pkl", "wb") as f:
    pickle.dump(summary_model, f)

with open("summary_vectorizer.pkl", "wb") as f:
    pickle.dump(summary_vectorizer, f)

print("✅ Models trained: risk classifier + summary retriever")

