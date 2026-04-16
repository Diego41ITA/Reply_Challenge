

from fastapi import FastAPI
import pandas as pd
from pathlib import Path
import requests
import json
import os
from dotenv import load_dotenv

app = FastAPI()

DATA_PATH = Path("../../data/The_Truman_Show_train/locations.json")

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
        data = json.load(f)
    df = pd.DataFrame(data)
    locations_data = df.to_dict(orient="records")
    # Compose detailed system prompt for location fraud detection
    system_prompt = (
        "You are a location anomaly detection expert. Given a list of user location records, identify the biotag values that are likely fraudulent. "
        "You must consider the following features for each user/location:\n"
        "1. Impossible jumps (speed outliers): flag if a user moves at a speed > 1000 km/h between two consecutive locations.\n"
        "2. Invalid coordinates: flag if latitude is not in [-90, 90] or longitude is not in [-180, 180].\n"
        "3. Rare country visits: flag if a user visits a country (or city) in <1% of their records.\n"
        "4. Teleportation: flag if a user appears in two distant cities (>300km apart) within 2 hours.\n"
        "5. Night-time outlier: flag if a user is far from their usual city between 12am-5am.\n"
        "6. Location in sea/uninhabited area: flag if city is missing or empty.\n"
        "7. Rare city visits: flag if a user visits a city in <1% of their records.\n"
        "Return ONLY a JSON object with a key 'fraudulent_ids' containing a list of biotag values you consider fraudulent based on these features."
    )
    user_content = json.dumps(locations_data)
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
    ai_json = json.loads(ai_content)
    return ai_json
