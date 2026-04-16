

import requests
from pathlib import Path
import json
import os
from dotenv import load_dotenv


AGENT_ENDPOINTS = {
    "transactions": "http://localhost:8001/detect",
    "users": "http://localhost:8002/detect",
    "locations": "http://localhost:8003/detect",
    "messages": "http://localhost:8005/detect",
    "combined": "http://localhost:8006/detect"
}


OUTPUT_PATH = Path("../output/suspected_frauds.txt")


# Load environment variables from .env file
load_dotenv()

# Azure OpenAI configuration (from environment)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")


def collect_fraudulent_ids():
    agent_results = {}
    for name, url in AGENT_ENDPOINTS.items():
        try:
            resp = requests.post(url)
            data = resp.json()
            if name == "combined":
                agent_results[name] = data.get("fraudulent", {})
            else:
                agent_results[name] = data.get("fraudulent_ids", [])
        except Exception as e:
            print(f"Error contacting {name} agent: {e}")
            agent_results[name] = []
    return agent_results

def main():
    agent_results = collect_fraudulent_ids()
    # Compose system prompt for final validation
    system_prompt = (
        "You are a fraud validation expert. You are given the results of multiple specialized agents (transactions, users, locations, messages, combined), each providing a list of suspected fraudulent IDs or user IDs. "
        "Your task is to review all these results together and, using the context, produce a final validated list of fraud IDs. "
        "Consider cross-agent signals, overlaps, and context. Return ONLY a JSON object with a key 'final_fraudulent_ids' containing the final list of fraud IDs (strings or user IDs) you consider truly fraudulent."
    )
    user_content = json.dumps(agent_results)
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
    response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    result = response.json()
    ai_content = result["choices"][0]["message"]["content"]
    try:
        ai_json = json.loads(ai_content)
        final_ids = ai_json.get("final_fraudulent_ids", [])
    except Exception:
        final_ids = []
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write("=== FINAL VALIDATED FRAUDULENT IDS ===\n")
        for tid in final_ids:
            f.write(f"{tid}\n")
        f.write("\n=== RAW AGENT RESULTS ===\n")
        for agent, results in agent_results.items():
            f.write(f"--- {agent.upper()} AGENT ---\n")
            if isinstance(results, dict):
                for uid, frauds in results.items():
                    f.write(f"{uid}: {frauds}\n")
            else:
                for tid in results:
                    f.write(f"{tid}\n")
            f.write("\n")
    print(f"Wrote final validated fraud IDs and all agent results to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
