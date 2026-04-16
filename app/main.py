from fastapi import FastAPI
from app.orchestrator import build_graph
from app.core.langfuse import (
    langfuse_client,
    generate_session_id
)

app = FastAPI()
graph = build_graph()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect")
def detect(payload: dict):

    session_id = generate_session_id()

    # IMPORTANT: grouping per challenge
    langfuse_client.update_current_trace(
        session_id=session_id
    )

    result = graph.invoke({
        "transactions": payload.get("transactions", []),
        "users": payload.get("users", []),
        "locations": payload.get("locations", []),
        "messages": payload.get("messages", [])
    })

    langfuse_client.flush()

    return {
        "session_id": session_id,
        "result": result
    }