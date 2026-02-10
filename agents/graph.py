"""LangGraph agent graph — linear pipeline: retrieve → synthesize → respond."""

import logging
from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents.retrieval import retrieve
from agents.synthesis import synthesize
from agents.responder import respond

logger = logging.getLogger(__name__)


class AgentState(TypedDict, total=False):
    query: str
    retrieved_posts: list[dict]
    synthesis: str
    response: str


def build_graph() -> StateGraph:
    """Build and compile the LangGraph agent graph."""
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve)
    graph.add_node("synthesize", synthesize)
    graph.add_node("respond", respond)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "synthesize")
    graph.add_edge("synthesize", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


# Singleton compiled graph
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_graph()
        logger.info("LangGraph agent compiled")
    return _agent


def query_agent(user_query: str) -> str:
    """Run a user query through the agent and return the response text."""
    agent = get_agent()
    result = agent.invoke({"query": user_query})
    return result.get("response", "Sorry, I couldn't generate a response.")
