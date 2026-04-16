from app.agents.base import build_agent
from app.core.prompts import TRANSACTIONS_PROMPT

def transactions_agent():
    return build_agent(TRANSACTIONS_PROMPT)