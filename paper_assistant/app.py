"""Paper Assistant Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from core.llm_client import is_configured
from core.paper_storage import ensure_directories, get_paper_by_id, list_papers
from core.ui import apply_page_style, page_header, sidebar_nav


st.set_page_config(
    page_title="论文阅读辅助器",
    layout="wide",
)

ensure_directories()
apply_page_style()
sidebar_nav("home")
papers = list_papers()
current = get_paper_by_id(st.session_state.get("selected_paper_id"))

page_header(
    "论文阅读辅助器",
    "本地论文入库、DeepSeek 宏观解读、逐段精读、批注和 Markdown 学习总结生成。",
    stats=[
        ("论文", str(len(papers))),
        ("DeepSeek", "Ready" if is_configured() else "Missing"),
        ("当前论文", "已选择" if current else "未选择"),
    ],
)

left, right = st.columns([0.58, 0.42], gap="large")

with left:
    with st.container(border=True):
        st.subheader("📋 建议流程")
        papers_count = len(list_papers())
        has_paper = current is not None

        steps = [
            (1, "上传论文 PDF 到文献库", "📚", papers_count > 0),
            (2, "运行宏观解读，获取论文概览", "📖", False),
            (3, "逐段精读，深入理解每个段落", "🔍", False),
            (4, "导出学习笔记，保存至本地", "📝", False),
        ]
        for num, label, icon, done in steps:
            status_icon = "✅" if done else ""
            st.markdown(
                f'<div class="pa-checklist-item">'
                f'<span class="pa-checklist-num">{num}</span>'
                f'<span>{icon} {label}</span>'
                f'<span class="pa-checklist-status">{status_icon}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        st.subheader("💾 本地数据")
        st.markdown(
            """
            <span class="pa-pill">📄 papers/ 存放 PDF</span>
            <span class="pa-pill">🏷️ annotations/ 存放批注</span>
            <span class="pa-pill">📝 notes/ 存放学习总结</span>
            """,
            unsafe_allow_html=True,
        )

with right:
    with st.container(border=True):
        st.subheader("✅ 启动检查")
        checks = [
            ("本地目录", "已创建", "✅"),
            (
                "DeepSeek Key",
                "已配置" if is_configured() else "未配置",
                "✅" if is_configured() else "⚠️",
            ),
            (
                "当前论文",
                "已选择" if current else "未选择",
                "✅" if current else "",
            ),
        ]
        for name, status, icon in checks:
            ok = "✅" in icon
            status_color = "var(--pa-accent)" if ok else "var(--pa-warm)"
            st.markdown(
                f'<div class="pa-checklist-item">'
                f'<span style="min-width:1.5rem">{icon}</span>'
                f'<strong>{name}</strong>'
                f'<span style="color:{status_color};margin-left:auto">{status}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if not is_configured():
            st.warning("请复制 `.env.example` 为 `.env`，并设置 `DEEPSEEK_API_KEY`。")

    if current:
        with st.container(border=True):
            st.subheader("📌 当前论文")
            st.markdown(f"**{current.get('title', 'Untitled Paper')}**")
            meta_parts = []
            if current.get("category"):
                meta_parts.append(f"分类：{current['category']}")
            if current.get("doi"):
                meta_parts.append(f"DOI：{current['doi']}")
            if current.get("filename"):
                meta_parts.append(f"文件：{current['filename']}")
            st.caption(" | ".join(meta_parts))

            col1, col2 = st.columns(2, gap="small")
            with col1:
                if st.button("宏观解读", use_container_width=True, type="primary"):
                    st.switch_page("pages/2_macro_reading.py")
            with col2:
                if st.button("逐段精读", use_container_width=True):
                    st.switch_page("pages/3_detail_reading.py")
