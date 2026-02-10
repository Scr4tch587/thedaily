"""Streamlit chart components — NYT-styled data visualizations."""

import json
import logging

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.settings import CHARTS_DATA_PATH

logger = logging.getLogger(__name__)

NYT_ACCENT = "#326891"
NYT_GRAY = "#666666"
NYT_LIGHT = "#E8E8E8"
NYT_BLACK = "#121212"


def _nyt_bar(fig, height=280):
    """Apply NYT-style layout to a bar chart."""
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Georgia, serif", color=NYT_BLACK, size=11),
        xaxis=dict(showticklabels=False, showgrid=False, linecolor=NYT_LIGHT),
        yaxis=dict(
            tickfont=dict(family="Libre Franklin, sans-serif", size=11, color=NYT_GRAY),
            linecolor=NYT_LIGHT,
        ),
        showlegend=False,
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
    """Render all data sections."""
    data = _load_charts_data()
    if data is None:
        st.markdown("""
        <p class="summary-text" style="color: #999; font-style: italic;">
            No data available yet. Run the pipeline to generate visualizations.
        </p>
        """, unsafe_allow_html=True)
        return

    _render_top_stories(data.get("top_stories", []))
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    _render_trending_topics(data.get("trending_topics", {}))
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    _render_hot_discussions(data.get("hot_discussions", []))
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    _render_domain_leaderboard(data.get("domain_leaderboard", []))
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    _render_story_types(data.get("story_type_breakdown", {}))


def _render_top_stories(stories: list[dict]):
    """Ranked list of top 5 stories."""
    if not stories:
        return

    st.markdown('<div class="headline-sm">Top Stories</div>', unsafe_allow_html=True)

    for i, s in enumerate(stories[:5], 1):
        title = s["title"][:80]
        hn_url = s.get("hn_url", "")
        score = s.get("score", 0)
        comments = s.get("num_comments", 0)

        st.markdown(f"""
        <div style="padding: 0.35rem 0; border-bottom: 1px solid #F0F0F0; display: flex; gap: 0.6rem;">
            <span style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.5rem;
                         font-weight: 300; color: #DDD; line-height: 1; min-width: 1.2rem;">{i}</span>
            <div>
                <a href="{hn_url}" target="_blank"
                   style="font-family: 'Libre Franklin', sans-serif; font-size: 0.82rem;
                          font-weight: 500; color: #121212 !important; line-height: 1.35;
                          text-decoration: none !important;">{title}</a>
                <div class="meta-text" style="margin-top: 2px;">{score} pts&ensp;&middot;&ensp;{comments} comments</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_trending_topics(topics: dict):
    """Horizontal bar chart of trending topics."""
    if not topics:
        return

    st.markdown('<div class="headline-sm">What\'s Trending</div>', unsafe_allow_html=True)

    df = pd.DataFrame([
        {"Topic": topic, "Stories": info["count"]}
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
    _nyt_bar(fig, height=max(180, len(df) * 32))
    st.plotly_chart(fig, use_container_width=True)


def _render_hot_discussions(discussions: list[dict]):
    """List of most debated stories."""
    if not discussions:
        return

    st.markdown('<div class="headline-sm">Hot Discussions</div>', unsafe_allow_html=True)
    st.markdown("""
    <p class="meta-text" style="margin-bottom: 0.3rem;">Highest comment-to-score ratio</p>
    """, unsafe_allow_html=True)

    for d in discussions[:5]:
        title = d["title"][:75]
        hn_url = d.get("hn_url", "")
        score = d.get("score", 0)
        comments = d.get("num_comments", 0)
        ratio = d.get("ratio", 0)

        st.markdown(f"""
        <div style="padding: 0.3rem 0; border-bottom: 1px solid #F0F0F0;">
            <a href="{hn_url}" target="_blank"
               style="font-family: 'Libre Franklin', sans-serif; font-size: 0.8rem;
                      font-weight: 500; color: #121212 !important; line-height: 1.35;
                      text-decoration: none !important;">{title}</a>
            <div class="meta-text" style="margin-top: 2px;">
                {comments} comments&ensp;&middot;&ensp;{score} pts&ensp;&middot;&ensp;{ratio}x ratio
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_domain_leaderboard(domains: list[dict]):
    """Bar chart of top linked domains."""
    if not domains:
        return

    st.markdown('<div class="headline-sm">Where Links Point</div>', unsafe_allow_html=True)

    df = pd.DataFrame(domains).sort_values("count", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["domain"],
        x=df["count"],
        orientation="h",
        marker_color=NYT_BLACK,
        text=df["count"],
        textposition="outside",
        textfont=dict(family="Libre Franklin, sans-serif", size=10, color=NYT_GRAY),
    ))
    _nyt_bar(fig, height=max(160, len(df) * 28))
    st.plotly_chart(fig, use_container_width=True)


def _render_story_types(types: dict):
    """Simple breakdown of Show HN / Ask HN / Stories."""
    if not types:
        return

    st.markdown('<div class="headline-sm">Story Types</div>', unsafe_allow_html=True)

    total = sum(types.values())
    cols = st.columns(len(types))
    for col, (label, count) in zip(cols, types.items()):
        pct = round(100 * count / total) if total else 0
        col.markdown(f"""
        <div style="text-align: center; padding: 0.4rem 0;">
            <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.5rem;
                        font-weight: 700; color: #121212;">{count}</div>
            <div style="font-family: 'Libre Franklin', sans-serif; font-size: 0.6rem;
                        text-transform: uppercase; letter-spacing: 1px; color: #999;">{label}</div>
            <div style="font-family: 'Libre Franklin', sans-serif; font-size: 0.65rem;
                        color: #CCC;">{pct}%</div>
        </div>
        """, unsafe_allow_html=True)
