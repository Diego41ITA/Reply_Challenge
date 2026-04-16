
from fastapi import FastAPI
from pathlib import Path
import pandas as pd
import json
from collections import defaultdict

import requests
import os
from dotenv import load_dotenv

app = FastAPI()

DATA_DIR = Path("../../data/The_Truman_Show_train")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/detect")
def detect():
    # Load all datasets
    users = json.load(open(DATA_DIR / "users.json"))
    transactions = pd.read_csv(DATA_DIR / "transactions.csv")
    locations = json.load(open(DATA_DIR / "locations.json"))
    mails = json.load(open(DATA_DIR / "mails.json"))
    sms = json.load(open(DATA_DIR / "sms.json"))

    # Index all data by user (assuming user_id or similar field exists)
    user_data = defaultdict(lambda: {"transactions": [], "locations": [], "mails": [], "sms": [], "profile": {}})
    # Map users
    for idx, u in enumerate(users):
        user_data[idx]["profile"] = u
    # Map transactions (assume 'user_id' field exists)
    for _, row in transactions.iterrows():
        uid = int(row.get("user_id", -1))
        if uid >= 0:
            user_data[uid]["transactions"].append(row.to_dict())
    # Map locations (assume 'user_id' field exists)
    for loc in locations:
        uid = int(loc.get("user_id", -1))
        if uid >= 0:
            user_data[uid]["locations"].append(loc)
    # Map mails (assume 'user_id' field exists)
    for mail in mails:
        uid = int(mail.get("user_id", -1))
        if uid >= 0:
            user_data[uid]["mails"].append(mail)
    # Map sms (assume 'user_id' field exists)
    for s in sms:
        uid = int(s.get("user_id", -1))
        if uid >= 0:
            user_data[uid]["sms"].append(s)

    # Use Azure OpenAI for holistic fraud detection
    # Prepare data for AI
    ai_input = {uid: data for uid, data in user_data.items()}
    system_prompt = (
        "You are a holistic fraud detection expert. For each user, you are given their profile, transactions, locations, mails, and sms. "
        "For each user, analyze all available data and return a list of fraud labels for that user. "
        "Consider transaction outliers, rapid repeats, new recipients, location anomalies, phishing in mails/sms, and user profile risks. "
        "Return ONLY a JSON object with a key 'fraudulent' mapping user indices to a list of fraud labels (e.g., {\"0\": [\"tx_123_amount_outlier\", ...]})."
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(ai_input)}
        ]
    }
    # Load environment variables from .env file
    load_dotenv()
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    headers = {
        "api-key": AZURE_OPENAI_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    result = response.json()
    ai_content = result["choices"][0]["message"]["content"]
    try:
        ai_json = json.loads(ai_content)
        return {"fraudulent": ai_json.get("fraudulent", {})}
    except Exception:
        return {"fraudulent": {}}
