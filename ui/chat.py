"""Streamlit chat component — NYT-styled message history and agent integration."""

import streamlit as st

from agents.graph import query_agent


def render_chat():
    """Render the main chat interface in a newspaper-style column."""
    # Initialize message history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Welcome message if no history
    if not st.session_state.messages:
        st.markdown("""
        <div class="headline-lg">What's happening in tech?</div>
        <p class="summary-text">
            Ask about today's breakthroughs, trending tools, AI developments,
            or anything from the latest discussions on Hacker News.
        </p>
        """, unsafe_allow_html=True)

    # Display message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about today's tech news..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting today's briefing..."):
                try:
                    response = query_agent(prompt)
                except Exception as e:
                    response = (
                        f"**Unable to retrieve briefing.** {e}\n\n"
                        "Ensure the pipeline has run at least once and API keys are configured."
                    )
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
