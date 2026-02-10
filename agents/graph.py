"""LangGraph agent graph — retrieve → synthesize+respond."""

import logging
from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents.retrieval import retrieve
from agents.synthesis import synthesize_and_respond

logger = logging.getLogger(__name__)


class AgentState(TypedDict, total=False):
    query: str
    chat_history: list[dict]
    retrieved_posts: list[dict]
    response: str


def build_graph() -> StateGraph:
    """Build and compile the LangGraph agent graph."""
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve)
    graph.add_node("respond", synthesize_and_respond)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_graph()
        logger.info("LangGraph agent compiled")
    return _agent


def query_agent(user_query: str, chat_history: list[dict] | None = None) -> str:
    """Run a user query through the agent and return the response text."""
    agent = get_agent()
    result = agent.invoke({
        "query": user_query,
        "chat_history": chat_history or [],
    })
    return result.get("response", "Sorry, I couldn't generate a response.")
