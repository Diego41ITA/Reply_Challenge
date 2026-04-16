import pandas as pd
import json
import requests

# 1. LOAD CSV
df = pd.read_csv("data/transactions.csv")

transactions = df.to_dict(orient="records")

# 2. LOAD altri file (se li hai)
with open("data/users.json") as f:
    users = json.load(f)

with open("data/locations.json") as f:
    locations = json.load(f)

with open("data/mails.json") as f:
    mails = json.load(f)

with open("data/sms.json") as f:
    sms = json.load(f)

# 3. PAYLOAD per API
payload = {
    "transactions": transactions,
    "users": users,
    "locations": locations,
    "messages": {
        "mails": mails,
        "sms": sms
    }
}

# 4. CALL FASTAPI
response = requests.post(
    "http://localhost:8000/detect",
    json=payload
)

print("STATUS:", response.status_code)
print(json.dumps(response.json(), indent=2))