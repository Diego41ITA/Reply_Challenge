from Code.agents.base import build_agent
from Code.core.prompts import JUDGE_PROMPT

def judge_agent():
    return build_agent(JUDGE_PROMPT)