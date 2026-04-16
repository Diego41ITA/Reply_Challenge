from fastapi import FastAPI
import json
from pathlib import Path
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import re

app = FastAPI()

import os
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "The_Truman_Show_train" / "users.json"
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
    with open(DATA_PATH, "r") as f:
        users = json.load(f)
    # Compose detailed system prompt for user fraud detection
    system_prompt = (
        "You are a user anomaly detection expert. Given a list of user records, identify the user indices (user_0, user_1, etc.) that are likely fraudulent. "
        "You must consider the following features for each user:\n"
        "1. Extremely low or high salary (outliers): flag if salary is more than 3 standard deviations from the mean.\n"
        "2. Missing or malformed IBAN: flag if IBAN is missing, too short, or does not start with two letters.\n"
        "3. Suspicious residence: flag if residence latitude or longitude is out of valid range.\n"
        "4. High travel frequency: flag if description mentions frequent travel.\n"
        "5. High phishing susceptibility: flag if description mentions high phishing risk.\n"
        "6. Missing critical fields: flag if any of first_name, last_name, birth_year, salary, job, iban, or residence is missing or empty.\n"
        "Return ONLY a JSON object with a key 'fraudulent_ids' containing a list of user indices (e.g., user_0, user_1) you consider fraudulent based on these features. DO NOT return any reasons, explanations, or extra text. Only the JSON object."
    )
    user_content = json.dumps(users)
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
