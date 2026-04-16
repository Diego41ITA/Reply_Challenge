from app.agents.base import build_agent
from app.core.prompts import JUDGE_PROMPT

def judge_agent():
    return build_agent(JUDGE_PROMPT)