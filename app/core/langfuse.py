import os
import ulid
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler


langfuse_client = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://challenges.reply.com/langfuse")
)


def generate_session_id():
    return f"{os.getenv('TEAM_NAME','team')}-{ulid.new().str}"


def get_langfuse_handler():
    # IMPORTANT: EXACT pattern from tutorial
    return CallbackHandler()