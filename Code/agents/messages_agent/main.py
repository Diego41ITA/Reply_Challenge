import re

def is_suspicious_link(text):
    pass
def fuzzy_domain_match(domain, official_domains, threshold=0.8):
    # Dummy implementation to fix IndentationError
    return False
def is_urgent(text):
    pass
def spoofed_sender(sender):
    pass
def sender_name_domain_mismatch(mail):
    pass
def suspicious_attachment(mail):
    pass
def reply_to_mismatch(mail):
    pass

from fastapi import FastAPI
import json
from pathlib import Path
import requests

app = FastAPI()

MAILS_PATH = Path("../../data/The_Truman_Show_train/mails.json")
SMS_PATH = Path("../../data/The_Truman_Show_train/sms.json")

# Load environment variables from .env file
import os
from dotenv import load_dotenv
load_dotenv()
# Azure OpenAI configuration (from environment)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/detect")
def detect():
    mails = []
    if MAILS_PATH.exists():
        with open(MAILS_PATH, "r") as f:
            mails = json.load(f)
    sms_list = []
    if SMS_PATH.exists():
        with open(SMS_PATH, "r") as f:
            sms_list = json.load(f)
    # Compose detailed system prompt for message fraud detection
    system_prompt = (
        "You are a message anomaly detection expert. Given a list of email and SMS records, identify the indices (mail_0, sms_0, etc.) that are likely fraudulent. "
        "You must consider the following features for each message:\n"
        "1. Suspicious links: flag if the message contains links to suspicious or lookalike domains.\n"
        "2. Urgent or phishing language: flag if the message contains urgent or phishing-related keywords, especially if excessive.\n"
        "3. Spoofed sender: flag if the sender domain is similar to but not exactly an official domain.\n"
        "4. Sender name/domain mismatch: flag if the sender name does not match the domain.\n"
        "5. Suspicious attachment: flag if the message mentions a suspicious attachment type.\n"
        "6. Reply-to mismatch: flag if the reply-to address is different from the sender.\n"
        "7. Unusual time: flag if the message is sent at a suspicious hour (e.g., late night for business mail).\n"
        "8. Suspicious HTML: flag if the message contains hidden links or obfuscated text.\n"
        "9. Repeated/mass message: flag if the same message is sent multiple times.\n"
        "10. Payment or sensitive info request: flag if the message requests sensitive information.\n"
        "Return ONLY a JSON object with a key 'fraudulent_ids' containing a list of indices (e.g., mail_0, sms_0) you consider fraudulent based on these features. DO NOT return any reasons, explanations, or extra text. Only the JSON object."
    )
    # Prepare data for AI
    data = {"mails": mails, "sms": sms_list}
    user_content = json.dumps(data)
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
    try:
        response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Azure OpenAI API request failed: {e}\nResponse: {getattr(e.response, 'text', None)}")
        return {"error": f"Azure OpenAI API request failed: {str(e)}"}

    try:
        result = response.json()
    except Exception as e:
        print(f"Failed to parse JSON from Azure OpenAI response: {response.text}")
        return {"error": "Failed to parse JSON from Azure OpenAI response", "response": response.text}

    ai_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    print(f"Raw AI response content: {ai_content}")
    ai_content = ai_content.strip()
    if ai_content.startswith("```json"):
        ai_content = re.sub(r"^```json\\n?", "", ai_content)
    if ai_content.endswith("```"):
        ai_content = re.sub(r"```$", "", ai_content)
    ai_content = ai_content.strip()
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
