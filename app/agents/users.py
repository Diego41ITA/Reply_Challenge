from app.agents.base import build_agent
from app.core.prompts import USERS_PROMPT

def users_agent():
    return build_agent(USERS_PROMPT)