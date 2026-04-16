from app.agents.base import build_agent
from app.core.prompts import LOCATIONS_PROMPT

def locations_agent():
    return build_agent(LOCATIONS_PROMPT)