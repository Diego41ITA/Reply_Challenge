from Code.agents.base import build_agent
from Code.core.prompts import TRANSACTIONS_PROMPT

def transactions_agent():
    return build_agent(TRANSACTIONS_PROMPT)