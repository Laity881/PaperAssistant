"""Paper Assistant Streamlit entry point."""

from __future__ import annotations

import html

import streamlit as st

from core.llm_client import get_chat_model_label, is_configured
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
model_name = get_chat_model_label()


def _action_tile(title: str, desc: str, page: str, *, primary: bool = False) -> None:
    st.markdown(
        f"""
        <div class="pa-action-copy">
            <div class="pa-action-title">{html.escape(title)}</div>
            <div class="pa-action-desc">{html.escape(desc)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        title,
        type="primary" if primary else "secondary",
        use_container_width=True,
        key=f"home_action_{page}",
    ):
        st.switch_page(page)


macro_done = False
detail_count = 0
learning_done = False
if current:
    paper_id = current["id"]
    macro_done = bool(st.session_state.get(f"macro_history_{paper_id}", []))
    detail_count = len(st.session_state.get(f"detail_records_{paper_id}", {}))
    learning_done = bool(st.session_state.get(f"learning_pack_{paper_id}", ""))

page_header(
    "论文阅读辅助器",
    "围绕入库、通读、精读、学习包和笔记导出构建的一体化论文学习工作台。",
    stats=[
        ("论文", str(len(papers))),
        ("Chat 模型", model_name),
        ("API", "Ready" if is_configured() else "Missing"),
        ("当前论文", "已选择" if current else "未选择"),
    ],
)

top_left, top_right = st.columns([0.62, 0.38], gap="large")

with top_left:
    with st.container(border=True):
        st.markdown('<div class="pa-section-eyebrow">Current Paper</div>', unsafe_allow_html=True)
        if current:
            title = html.escape(current.get("title", "Untitled Paper"))
            category = html.escape(current.get("category", "未分类"))
            filename = html.escape(current.get("filename", ""))
            st.markdown(
                f"""
                <div class="pa-focus-title">{title}</div>
                <div class="pa-focus-meta">分类：{category} | 文件：{filename}</div>
                <div class="pa-progress-row">
                    <span class="pa-progress-chip {'is-done' if macro_done else ''}">宏观解读</span>
                    <span class="pa-progress-chip {'is-done' if detail_count else ''}">精读 {detail_count} 段</span>
                    <span class="pa-progress-chip {'is-done' if learning_done else ''}">学习包</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="pa-empty">
                    当前还没有选择论文。先进入文献库上传 PDF 或通过 DOI 导入，之后这里会显示阅读进度和学习入口。
                </div>
                """,
                unsafe_allow_html=True,
            )

        action_cols = st.columns(4, gap="small")
        with action_cols[0]:
            _action_tile("文献库", "上传、检索、分类", "pages/1_library.py", primary=not current)
        with action_cols[1]:
            _action_tile("宏观解读", "摘要、架构、创新点", "pages/2_macro_reading.py", primary=bool(current))
        with action_cols[2]:
            _action_tile("逐章节精读", "翻译、拆解、问答", "pages/3_detail_reading.py")
        with action_cols[3]:
            _action_tile("学习中心", "术语、自测、复习", "pages/5_learning_center.py")

with top_right:
    with st.container(border=True):
        st.markdown('<div class="pa-section-eyebrow">System Check</div>', unsafe_allow_html=True)
        checks = [
            ("本地目录", "已创建", True),
            ("Chat API Key", "已配置" if is_configured() else "未配置", is_configured()),
            ("模型", model_name, True),
            ("当前论文", "已选择" if current else "未选择", bool(current)),
        ]
        for name, status, ok in checks:
            st.markdown(
                f"""
                <div class="pa-check-row">
                    <span class="pa-status-dot {'ok' if ok else 'warn'}"></span>
                    <span class="pa-check-name">{html.escape(name)}</span>
                    <span class="pa-check-status">{html.escape(status)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if not is_configured():
            st.warning("请在 `.env` 中设置 `CHAT_API_KEY`，或继续使用兼容的 `DEEPSEEK_API_KEY`。")

mid_left, mid_right = st.columns([0.5, 0.5], gap="large")

with mid_left:
    with st.container(border=True):
        st.markdown('<div class="pa-section-eyebrow">Reading Flow</div>', unsafe_allow_html=True)
        steps = [
            ("01", "入库与分类", "把 PDF、DOI、标题和分类整理好，形成可检索的文献库。", bool(papers)),
            ("02", "宏观通读", "先拿到研究问题、论文结构和创新点，避免直接陷入细节。", macro_done),
            ("03", "逐章节精读", "围绕当前章节生成翻译、解释、疑问和问答记录。", detail_count > 0),
            ("04", "学习巩固", "生成术语表、自测题和复习计划，沉淀长期笔记。", learning_done),
        ]
        for num, title, desc, done in steps:
            st.markdown(
                f"""
                <div class="pa-timeline-item {'is-done' if done else ''}">
                    <div class="pa-timeline-num">{num}</div>
                    <div>
                        <div class="pa-timeline-title">{html.escape(title)}</div>
                        <div class="pa-timeline-desc">{html.escape(desc)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with mid_right:
    with st.container(border=True):
        st.markdown('<div class="pa-section-eyebrow">Local Workspace</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="pa-data-grid">
                <div><strong>论文/</strong><span>PDF 原文与分类目录</span></div>
                <div><strong>批注/</strong><span>高亮、批注与定位数据</span></div>
                <div><strong>笔记/</strong><span>Markdown 学习总结</span></div>
                <div><strong>会话</strong><span>阅读进度、问答和学习包</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "当前进度："
            f"宏观解读 {'已完成' if macro_done else '未生成'}，"
            f"精读 {detail_count} 段，"
            f"学习包 {'已生成' if learning_done else '未生成'}。"
        )
