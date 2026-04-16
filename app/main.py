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

    # 1. Create session ID (used for grouping in Langfuse)
    session_id = generate_session_id()

    # 2. Run graph (Langfuse tracking happens inside nodes via CallbackHandler)
    result = graph.invoke({
        "transactions": payload.get("transactions", []),
        "users": payload.get("users", []),
        "locations": payload.get("locations", []),
        "messages": payload.get("messages", {})
    })

    # 3. Flush Langfuse traces (IMPORTANT)
    langfuse_client.flush()

    return {
        "session_id": session_id,
        "result": result
    }