"""Shared Streamlit UI helpers for Paper Assistant."""

from __future__ import annotations

import html

import streamlit as st

from .ui_css import LIGHT_THEME, DARK_THEME, assemble_css

READING_PANEL_HEIGHT = 680
COMPACT_PANEL_HEIGHT = 540


def apply_page_style() -> None:
    """Apply the current theme's CSS to the page."""

    theme_name = st.session_state.get("pa_theme", "light")
    theme = DARK_THEME if theme_name == "dark" else LIGHT_THEME
    st.markdown(
        f"<style>{assemble_css(theme)}</style>",
        unsafe_allow_html=True,
    )


def sidebar_nav(active: str = "") -> None:
    """Render a consistent dark application sidebar."""

    from .llm_client import CHAT_MODEL_OPTIONS, get_chat_model_label, get_chat_model_name, is_configured
    from .paper_storage import get_paper_by_id, list_papers

    labels = {
        "home": "首页",
        "library": "文献库",
        "macro": "宏观解读",
        "detail": "逐章节精读",
        "learning": "学习中心",
        "files": "文件管理",
    }
    current = get_paper_by_id(st.session_state.get("selected_paper_id"))
    papers = list_papers()
    api_status = "已配置" if is_configured() else "未配置"
    if "pa_chat_model" not in st.session_state:
        st.session_state["pa_chat_model"] = get_chat_model_label()
    model_name = get_chat_model_name()
    model_label = get_chat_model_label(model_name)

    with st.sidebar:
        st.markdown(
            """
            <div class="pa-brand">
                <div class="pa-brand-row">
                    <div class="pa-brand-mark">PA</div>
                    <div>
                        <div class="pa-brand-title">Paper Assistant</div>
                        <div class="pa-brand-subtitle">Research reading workspace</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if active:
            st.markdown(
                f'<div class="pa-active-page">当前工作区：{labels.get(active, active)}</div>',
                unsafe_allow_html=True,
            )

        st.page_link("app.py", label="🏠 首页")
        st.page_link("pages/1_library.py", label="📚 文献库")
        st.page_link("pages/2_macro_reading.py", label="📖 宏观解读")
        st.page_link("pages/3_detail_reading.py", label="🔍 逐章节精读")
        st.page_link("pages/5_learning_center.py", label="🎓 学习中心")
        st.page_link("pages/4_file_manager.py", label="📁 文件管理")

        st.divider()

        st.selectbox(
            "模型",
            list(CHAT_MODEL_OPTIONS),
            key="pa_chat_model",
            format_func=lambda item: "chat" if item == "chat" else "v4-pro",
            help="界面显示短名，调用 API 时会自动映射为受支持的模型 ID。",
        )

        # Theme toggle
        current_theme = st.session_state.get("pa_theme", "light")
        new_theme = st.selectbox(
            "主题",
            ["light", "dark"],
            index=0 if current_theme == "light" else 1,
            format_func=lambda x: "浅色模式" if x == "light" else "深色模式",
            label_visibility="collapsed",
        )
        if new_theme != current_theme:
            st.session_state["pa_theme"] = new_theme
            st.rerun()

        st.divider()
        st.metric("已入库论文", len(papers))
        st.markdown(
            f'<span class="pa-tag">Chat API：{api_status}</span>'
            f'<span class="pa-tag">模型：{html.escape(model_label)}</span>',
            unsafe_allow_html=True,
        )

        if current:
            title = html.escape(current.get("title", "Untitled Paper"))
            category = html.escape(current.get("category", "未分类"))
            doi = html.escape(current.get("doi") or "暂无")
            st.markdown(
                f"""
                <div class="pa-active-page">
                    <div style="font-weight:760;margin-bottom:.25rem;">当前论文</div>
                    <div style="line-height:1.45;">{title}</div>
                    <div style="color:#9aa4b2;font-size:.78rem;margin-top:.35rem;">
                        {category}<br/>DOI：{doi}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def page_header(
    title: str,
    subtitle: str,
    kicker: str = "Paper Assistant",
    stats: list[tuple[str, str]] | None = None,
) -> None:
    """Render a compact page header with optional stat chips."""

    stat_html = ""
    if stats:
        stat_html = '<div class="pa-head-stats">'
        for label, value in stats:
            stat_html += (
                '<div class="pa-stat">'
                f'<div class="pa-stat-label">{html.escape(label)}</div>'
                f'<div class="pa-stat-value">{html.escape(value)}</div>'
                "</div>"
            )
        stat_html += "</div>"

    st.markdown(
        f"""
        <div class="pa-page-head">
            <div>
                <div class="pa-kicker">{html.escape(kicker)}</div>
                <div class="pa-title">{html.escape(title)}</div>
                <div class="pa-subtitle">{html.escape(subtitle)}</div>
            </div>
            {stat_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel_title(title: str, meta: str = "") -> None:
    """Render a small panel title above a working surface."""

    st.markdown(
        f"""
        <div class="pa-panel-title">
            <div class="pa-panel-title-main">{html.escape(title)}</div>
            <div class="pa-panel-title-meta">{html.escape(meta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def paper_identity(paper: dict) -> None:
    """Render paper title and metadata in a compact strip."""

    title = html.escape(paper.get("title", "Untitled Paper"))
    category = html.escape(paper.get("category", "未分类"))
    doi = html.escape(paper.get("doi") or "暂无")
    filename = html.escape(paper.get("filename") or "暂无")

    st.markdown(
        f"""
        <div class="pa-paper-strip">
            <div>
                <div class="pa-paper-title">{title}</div>
                <div class="pa-meta">分类：{category} | DOI：{doi} | 文件：{filename}</div>
            </div>
            <div>
                <span class="pa-tag pa-tag-dark">Active Paper</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
