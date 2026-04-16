import sys
import pandas as pd
import json
import requests
import os
import numpy as np

# Ensure script works from its own directory
os.chdir(sys.path[0])


# =========================
# SAFE JSON CLEANER
# Fixes NaN / Infinity issues that break JSON serialization
# =========================
def safe_json(obj):
    if isinstance(obj, dict):
        return {k: safe_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [safe_json(v) for v in obj]

    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj

    return obj


# =========================
# 1. LOAD CSV (TRANSACTIONS)
# =========================
df = pd.read_csv("data/The_Truman_Show_train/transactions.csv")

# Replace invalid numeric values
df = df.replace([np.inf, -np.inf], np.nan)
df = df.where(pd.notnull(df), None)

transactions = df.to_dict(orient="records")
transactions = safe_json(transactions)


# =========================
# 2. LOAD OTHER FILES
# =========================
with open("data/The_Truman_Show_train/users.json") as f:
    users = json.load(f)

with open("data/The_Truman_Show_train/locations.json") as f:
    locations = json.load(f)

with open("data/The_Truman_Show_train/mails.json") as f:
    mails = json.load(f)

with open("data/The_Truman_Show_train/sms.json") as f:
    sms = json.load(f)


# Apply safety cleaning to all JSON inputs
users = safe_json(users)
locations = safe_json(locations)
mails = safe_json(mails)
sms = safe_json(sms)


# =========================
# 3. BUILD API PAYLOAD
# =========================
payload = {
    "transactions": transactions,
    "users": users,
    "locations": locations,
    "messages": {
        "mails": mails,
        "sms": sms
    }
}


# =========================
# 4. CALL FASTAPI ENDPOINT
# =========================
response = requests.post(
    "http://localhost:8000/detect",
    json=payload,
    timeout=120
)

# =========================
# 5. PRINT RESULT
# =========================
print("STATUS:", response.status_code)

try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print("RAW RESPONSE:", response.text)