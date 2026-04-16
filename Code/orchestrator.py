from langgraph.graph import StateGraph
from typing import TypedDict

from Code.agents.transactions import transactions_agent
from Code.agents.users import users_agent
from Code.agents.locations import locations_agent
from Code.agents.messages import messages_agent
from Code.agents.judge import judge_agent

from Code.core.langfuse import (
    get_langfuse_handler,
    langfuse_client,
    generate_session_id
)


class State(TypedDict):
    transactions: dict
    users: dict
    locations: dict
    messages: dict


# -------- nodes --------

def run_transactions(state):
    handler = get_langfuse_handler()

    return {
        "transactions": transactions_agent().invoke(
            {"input": state["transactions"]},
            config={"callbacks": [handler]}
        )
    }


def run_users(state):
    handler = get_langfuse_handler()

    return {
        "users": users_agent().invoke(
            {"input": state["users"]},
            config={"callbacks": [handler]}
        )
    }


def run_locations(state):
    handler = get_langfuse_handler()

    return {
        "locations": locations_agent().invoke(
            {"input": state["locations"]},
            config={"callbacks": [handler]}
        )
    }


def run_messages(state):
    handler = get_langfuse_handler()

    return {
        "messages": messages_agent().invoke(
            {"input": state["messages"]},
            config={"callbacks": [handler]}
        )
    }


def run_judge(state):
    handler = get_langfuse_handler()

    result = judge_agent().invoke(
        {"input": state},
        config={"callbacks": [handler]}
    )

    return {"result": result}


# -------- graph --------

def build_graph():
    graph = StateGraph(State)

    graph.add_node("transactions", run_transactions)
    graph.add_node("users", run_users)
    graph.add_node("locations", run_locations)
    graph.add_node("messages", run_messages)
    graph.add_node("judge", run_judge)

    graph.set_entry_point("transactions")

    graph.add_edge("transactions", "users")
    graph.add_edge("users", "locations")
    graph.add_edge("locations", "messages")
    graph.add_edge("messages", "judge")

    graph.set_finish_point("judge")

    return graph.compile()