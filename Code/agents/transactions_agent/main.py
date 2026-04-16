from fastapi import FastAPI
import pandas as pd
from pathlib import Path
import requests
import json
import os
from dotenv import load_dotenv
import re

app = FastAPI()

import os
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "The_Truman_Show_train" / "transactions.csv"
print(f"[INFO] DATA_PATH resolved to: {DATA_PATH}")

# Load environment variables from .env file
load_dotenv()
# Azure OpenAI configuration (from environment)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect")
def detect():
    if not DATA_PATH.exists():
        return {"fraudulent_ids": []}
    df = pd.read_csv(DATA_PATH)
    # Prepare data for Azure OpenAI
    transactions_data = df.to_dict(orient="records")
    # Compose detailed system prompt for fraud detection
    system_prompt = (
        "You are a financial fraud detection expert. Given a list of transaction records, identify the transaction_ids that are likely fraudulent. "
        "You must consider the following features for each transaction:\n"
        "1. Z-score anomaly detection for amount: flag transactions where the amount is an outlier (z-score > 3 or < -3).\n"
        "2. Time-of-day anomaly: flag transactions that occur at rare hours (hours with <1% of all transactions).\n"
        "3. Negative or very low balance after transaction: flag if balance_after < 0.\n"
        "4. Rapid repeated transactions: flag if the same sender and recipient transact more than once within 1 hour.\n"
        "5. New recipient for sender: flag the first time a sender transacts with a new recipient.\n"
        "6. Missing or malformed critical fields: flag if any of transaction_id, sender_id, recipient_id, amount, or timestamp is missing or malformed.\n"
        "7. Sudden large drop in balance: flag if the amount is more than 50% of the previous balance.\n"
        "8. Unusual payment method: flag if the sender uses a payment method different from their usual method.\n"
        "Return ONLY a JSON object with a key 'fraudulent_ids' containing a list of transaction_ids that you consider fraudulent based on these features. DO NOT return any reasons, explanations, or extra text. Only the JSON object."
    )
    user_content = json.dumps(transactions_data)
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    }
    headers = {
        "api-key": AZURE_OPENAI_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    # Extract the model's reply
    ai_content = result["choices"][0]["message"]["content"]
    print(f"Raw AI response content: {ai_content}")
    # Remove markdown code block if present
    cleaned = re.sub(r"```json|```", "", ai_content).strip()

    try:
        ai_json = json.loads(cleaned)
    except json.JSONDecodeError:
        ai_json = {}
    # Return only fraudulent object
    if isinstance(ai_json, dict) and "fraudulent_ids" in ai_json:
        return ai_json["fraudulent_ids"]

    return ai_json