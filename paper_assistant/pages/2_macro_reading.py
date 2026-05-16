"""Macro reading page: overview generation and contextual chat."""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from core.llm_client import (
    get_chat_model_label,
    stream_answer_macro_question,
    stream_macro_reading,
)
from core.note_exporter import export_study_note
from core.paper_storage import (
    ensure_directories,
    get_paper_by_id,
    list_papers,
    resolve_paper_path,
)
from core.pdf_utils import extract_text_from_pdf, render_pdf_viewer
from core.ui import (
    READING_PANEL_HEIGHT,
    apply_page_style,
    page_header,
    panel_title,
    paper_identity,
    sidebar_nav,
)


st.set_page_config(page_title="宏观解读", layout="wide")
ensure_directories()
apply_page_style()
sidebar_nav("macro")


@st.cache_data(show_spinner=False)
def _cached_pdf_text(path: str, mtime: float) -> str:
    return extract_text_from_pdf(path)


def _select_paper() -> dict | None:
    """Render a paper selector with search and store the selected paper id."""

    papers = list_papers()
    if not papers:
        st.info("📚 请先在**文献库**中上传或下载一篇论文。")
        if st.button("前往文献库", type="primary"):
            st.switch_page("pages/1_library.py")
        return None

    # Search filter
    search = st.text_input(
        "搜索论文",
        placeholder="输入标题关键词筛选...",
        key="macro_paper_search",
        label_visibility="collapsed",
    )
    if search:
        q = search.lower()
        papers = [
            p for p in papers
            if q in (p.get("title", "") or "").lower()
            or q in (p.get("category", "") or "").lower()
        ]
        if not papers:
            st.warning("没有匹配的论文。")
            return None

    paper_map = {paper["id"]: paper for paper in papers}
    ids = list(paper_map)
    current_id = st.session_state.get("selected_paper_id")
    index = ids.index(current_id) if current_id in ids else 0

    selected_id = st.selectbox(
        "选择论文",
        ids,
        index=index,
        format_func=lambda paper_id: (
            f"{paper_map[paper_id].get('title', 'Untitled Paper')[:60]} | "
            f"{paper_map[paper_id].get('category', '未分类')}"
        ),
        label_visibility="collapsed",
    )
    st.session_state["selected_paper_id"] = selected_id
    return get_paper_by_id(selected_id)


def _history_key(paper_id: str) -> str:
    return f"macro_history_{paper_id}"


def _show_chat(history: list[dict[str, str]]) -> None:
    if not history:
        st.markdown(
            '<div class="pa-empty">点击"生成宏观解读"后，这里会显示摘要、论文架构和创新点。后续追问也会保存在同一上下文中。</div>',
            unsafe_allow_html=True,
        )
        return

    for message in history:
        role = message.get("role", "assistant")
        with st.chat_message(role):
            st.markdown(message.get("content", ""))


def _export_controls(paper: dict, pdf_path: Path) -> None:
    paper_id = paper["id"]
    custom_key = f"custom_note_{paper_id}"
    with st.status("导出笔记", expanded=False, state="complete") as status:
        st.text_area(
            "学习笔记（可选）",
            key=custom_key,
            height=100,
            placeholder="写一些自己的总结和心得...",
            label_visibility="collapsed",
        )
        if st.button(
            "生成并导出总结",
            type="primary",
            use_container_width=True,
            key=f"export_macro_{paper_id}",
        ):
            with st.spinner("正在生成 Markdown 总结..."):
                result = export_study_note(
                    paper=paper,
                    macro_history=st.session_state.get(_history_key(paper_id), []),
                    detail_records=st.session_state.get(f"detail_records_{paper_id}", {}),
                    detail_history=st.session_state.get(f"detail_history_{paper_id}", []),
                    confusions=st.session_state.get(f"confusions_{paper_id}", []),
                    custom_note=st.session_state.get(custom_key, ""),
                    pdf_path=pdf_path,
                    use_llm=True,
                )
            status.update(label="导出完成", state="complete")
            st.toast(f"总结已保存至 {result['path']}")
            if result.get("llm_error"):
                st.warning(f"AI 整理失败，已保存原始结构化笔记：{result['llm_error']}")


page_header(
    "宏观解读",
    "在同一画布中并排阅读 PDF 与模型分析，长回答会留在右侧工作区内滚动。",
)
model_name = get_chat_model_label()

panel_title("当前对象", "选择要分析的论文")
with st.container(border=True):
    paper = _select_paper()
if paper is None:
    st.stop()

pdf_path = resolve_paper_path(paper)
paper_id = paper["id"]
history_key = _history_key(paper_id)
st.session_state.setdefault(history_key, [])

if not pdf_path.exists():
    st.error("PDF 文件不存在，请回到文献库检查。")
    st.stop()

paper_text = _cached_pdf_text(str(pdf_path), pdf_path.stat().st_mtime)

left, right = st.columns([0.6, 0.4], gap="large")

with left:
    with st.container(border=True):
        paper_identity(paper)

    # Reading stats
    word_count = len(paper_text.replace("\n", " ").split())
    est_read_mins = max(1, word_count // 250)
    st.markdown(
        f'<span class="pa-pill">约 {word_count:,} 词</span>'
        f'<span class="pa-pill">预计阅读 {est_read_mins} 分钟</span>'
        f'<span class="pa-pill">PDF 解析完成</span>',
        unsafe_allow_html=True,
    )

    panel_title("论文原文", "PDF / 文本阅读")
    with st.container(height=READING_PANEL_HEIGHT, border=True):
        rendered = render_pdf_viewer(pdf_path, height=READING_PANEL_HEIGHT - 32)
        if not rendered:
            text_tab, raw_tab = st.tabs(["格式化文本", "原始文本"])
            with text_tab:
                paragraphs = paper_text.split("\n\n")
                for para in paragraphs[:80]:
                    if para.strip():
                        st.markdown(
                            f'<div class="plain-para">{html.escape(para.strip()[:600])}</div>',
                            unsafe_allow_html=True,
                        )
                if len(paragraphs) > 80:
                    st.caption(f"... 共 {len(paragraphs)} 段，仅显示前 80 段")
            with raw_tab:
                st.text_area(
                    "论文全文",
                    value=paper_text[:30000],
                    height=READING_PANEL_HEIGHT - 120,
                    disabled=True,
                    label_visibility="collapsed",
                )

with right:
    panel_title(f"{model_name} 工作区", "宏观摘要、架构、创新点")
    action_cols = st.columns([0.55, 0.45], vertical_alignment="center")
    with action_cols[0]:
        run_macro = st.button(
            "生成宏观解读",
            type="primary",
            use_container_width=True,
            key=f"macro_start_{paper_id}",
        )
    with action_cols[1]:
        if st.button("清空本页对话", use_container_width=True, key=f"clear_macro_{paper_id}"):
            st.session_state[history_key] = []
            st.rerun()

    if run_macro:
        try:
            with st.status(f"{model_name} 正在分析论文...", expanded=True) as gen_status:
                gen_status.write("提取论文全文...")
                gen_status.write("生成宏观摘要...")
                with st.chat_message("assistant"):
                    answer = st.write_stream(stream_macro_reading(paper_text))
                gen_status.update(label="分析完成", state="complete")
            st.session_state[history_key].append(
                {"role": "assistant", "content": answer}
            )
            st.rerun()
        except Exception as exc:
            st.error(f"宏观解读失败：{exc}")
            if st.button("重试宏观解读", key=f"retry_macro_{paper_id}"):
                st.rerun()

    with st.container(height=READING_PANEL_HEIGHT, border=True):
        _show_chat(st.session_state[history_key])

    _export_controls(paper, pdf_path)

prompt = st.chat_input("追问这篇论文，例如：这个方法和 XX 方法有什么区别？")
if prompt:
    st.session_state[history_key].append({"role": "user", "content": prompt})
    try:
        with st.spinner(f"{model_name} 正在结合上下文回答..."):
            with st.chat_message("assistant"):
                answer = st.write_stream(
                    stream_answer_macro_question(
                        prompt,
                        paper_text,
                        st.session_state[history_key],
                    )
                )
        st.session_state[history_key].append({"role": "assistant", "content": answer})
    except Exception as exc:
        st.session_state[history_key].append(
            {
                "role": "assistant",
                "content": f"调用失败：{exc}\n\n请检查 API Key 或稍后重试。",
            }
        )
    st.rerun()
