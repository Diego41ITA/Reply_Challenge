from app.agents.base import build_agent
from app.core.prompts import MESSAGES_PROMPT

def messages_agent():
    return build_agent(MESSAGES_PROMPT)