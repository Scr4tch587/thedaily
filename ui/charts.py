"""Streamlit chart components — NYT-styled Plotly visualizations."""

import json
import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config.settings import CHARTS_DATA_PATH

logger = logging.getLogger(__name__)

# NYT-inspired color palette
NYT_BLACK = "#121212"
NYT_GRAY = "#666666"
NYT_LIGHT = "#E8E8E8"
NYT_ACCENT = "#326891"
NYT_BG = "#FAFAF8"


def _nyt_layout(fig, height=320):
    """Apply NYT-style layout to a Plotly figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Georgia, serif", color=NYT_BLACK, size=11),
        xaxis=dict(
            gridcolor=NYT_LIGHT,
            linecolor=NYT_LIGHT,
            tickfont=dict(family="Libre Franklin, sans-serif", size=10, color=NYT_GRAY),
        ),
        yaxis=dict(
            gridcolor=NYT_LIGHT,
            linecolor=NYT_LIGHT,
            tickfont=dict(family="Libre Franklin, sans-serif", size=10, color=NYT_GRAY),
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(family="Libre Franklin, sans-serif", size=9, color=NYT_GRAY),
            title_font=dict(family="Libre Franklin, sans-serif", size=9, color=NYT_GRAY),
        ),
    )
    return fig


def _load_charts_data() -> dict | None:
    if not CHARTS_DATA_PATH.exists():
        return None
    try:
        with open(CHARTS_DATA_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def render_charts():
    """Render all visualization sections."""
    data = _load_charts_data()
    if data is None:
        st.markdown("""
        <p class="summary-text" style="color: #999; font-style: italic;">
            No data available yet. Run the pipeline to generate visualizations.
        </p>
        """, unsafe_allow_html=True)
        return

    _render_trending_topics(data.get("trending_topics", {}))
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    _render_comment_engagement(data.get("comment_engagement", {}))
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    _render_score_distribution(data.get("score_distribution", []))


def _render_trending_topics(topics: dict):
    """Horizontal bar chart of trending topics."""
    if not topics:
        return

    st.markdown('<div class="headline-sm">What\'s Trending</div>', unsafe_allow_html=True)

    df = pd.DataFrame([
        {"Topic": topic, "Stories": info["count"], "Avg Score": info["avg_score"]}
        for topic, info in topics.items()
    ]).sort_values("Stories", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Topic"],
        x=df["Stories"],
        orientation="h",
        marker_color=NYT_ACCENT,
        text=df["Stories"],
        textposition="outside",
        textfont=dict(family="Libre Franklin, sans-serif", size=10, color=NYT_GRAY),
    ))
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(tickfont=dict(family="Libre Franklin, sans-serif", size=11)),
    )
    _nyt_layout(fig, height=max(180, len(df) * 32))
    st.plotly_chart(fig, use_container_width=True)


def _render_comment_engagement(engagement: dict):
    """Bar chart of comment count buckets."""
    if not engagement:
        return

    st.markdown('<div class="headline-sm">Discussion Engagement</div>', unsafe_allow_html=True)

    df = pd.DataFrame([
        {"Comments": bucket, "Stories": count}
        for bucket, count in engagement.items()
    ])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Comments"],
        y=df["Stories"],
        marker_color=NYT_BLACK,
        text=df["Stories"],
        textposition="outside",
        textfont=dict(family="Libre Franklin, sans-serif", size=10, color=NYT_GRAY),
    ))
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        yaxis=dict(showticklabels=False, showgrid=False),
        xaxis=dict(tickfont=dict(family="Libre Franklin, sans-serif", size=10)),
    )
    _nyt_layout(fig, height=220)
    st.plotly_chart(fig, use_container_width=True)


def _render_score_distribution(scores: list[int]):
    """Histogram of story scores with summary stats."""
    if not scores:
        return

    st.markdown('<div class="headline-sm">Score Distribution</div>', unsafe_allow_html=True)

    # Summary stats in newspaper style
    series = pd.Series(scores)
    col1, col2, col3, col4 = st.columns(4)
    for col, label, val in [
        (col1, "STORIES", len(scores)),
        (col2, "MEDIAN", int(series.median())),
        (col3, "MEAN", int(series.mean())),
        (col4, "HIGH", max(scores)),
    ]:
        col.markdown(f"""
        <div style="text-align: center; padding: 0.3rem 0;">
            <div style="font-family: 'Libre Franklin', sans-serif; font-size: 0.55rem;
                        text-transform: uppercase; letter-spacing: 1.5px; color: #999;">{label}</div>
            <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem;
                        font-weight: 700; color: #121212;">{val:,}</div>
        </div>
        """, unsafe_allow_html=True)

    df = pd.DataFrame({"Score": scores})
    fig = px.histogram(
        df, x="Score", nbins=25,
        color_discrete_sequence=[NYT_ACCENT],
    )
    fig.update_traces(marker_line_color=NYT_BG, marker_line_width=0.5)
    _nyt_layout(fig, height=220)
    st.plotly_chart(fig, use_container_width=True)
