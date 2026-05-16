"""Learning center: study plan, glossary, quiz, and review tracking."""

from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

from core.agent_tools import save_note_raw
from core.llm_client import get_chat_model_label, is_configured, stream_learning_pack
from core.paper_storage import (
    ensure_directories,
    get_paper_by_id,
    list_papers,
    resolve_paper_path,
)
from core.pdf_utils import extract_text_from_pdf
from core.ui import apply_page_style, page_header, panel_title, paper_identity, sidebar_nav


st.set_page_config(page_title="学习中心", layout="wide")
ensure_directories()
apply_page_style()
sidebar_nav("learning")


@st.cache_data(show_spinner=False)
def _cached_pdf_text(path: str, mtime: float) -> str:
    return extract_text_from_pdf(path)


def _select_paper() -> dict | None:
    papers = list_papers()
    if not papers:
        st.info("请先在文献库中上传或下载一篇论文。")
        if st.button("前往文献库", type="primary"):
            st.switch_page("pages/1_library.py")
        return None

    search = st.text_input(
        "搜索论文",
        placeholder="输入标题或分类关键词筛选...",
        key="learning_paper_search",
        label_visibility="collapsed",
    )
    if search:
        q = search.lower()
        papers = [
            paper
            for paper in papers
            if q in (paper.get("title", "") or "").lower()
            or q in (paper.get("category", "") or "").lower()
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
            f"{paper_map[paper_id].get('title', 'Untitled Paper')[:68]} | "
            f"{paper_map[paper_id].get('category', '未分类')}"
        ),
        label_visibility="collapsed",
        key="learning_selected_paper",
    )
    st.session_state["selected_paper_id"] = selected_id
    return get_paper_by_id(selected_id)


def _pack_key(paper_id: str) -> str:
    return f"learning_pack_{paper_id}"


def _score_key(paper_id: str, name: str) -> str:
    return f"learning_score_{paper_id}_{name}"


def _task_key(paper_id: str, index: int) -> str:
    return f"learning_task_{paper_id}_{index}"


def _note_key(paper_id: str, name: str) -> str:
    return f"learning_note_{paper_id}_{name}"


def _build_learning_note(paper: dict, pack: str, tasks: list[str]) -> str:
    paper_id = paper["id"]
    scores = {
        "术语掌握": st.session_state.get(_score_key(paper_id, "terms"), 0),
        "方法复述": st.session_state.get(_score_key(paper_id, "method"), 0),
        "实验理解": st.session_state.get(_score_key(paper_id, "experiment"), 0),
    }
    notes = {
        "一句话总结": st.session_state.get(_note_key(paper_id, "one_sentence"), "").strip(),
        "最不懂的问题": st.session_state.get(_note_key(paper_id, "hardest"), "").strip(),
        "可复述的创新点": st.session_state.get(_note_key(paper_id, "innovation"), "").strip(),
        "下一步行动": st.session_state.get(_note_key(paper_id, "next_action"), "").strip(),
    }
    task_lines = []
    for index, task in enumerate(tasks):
        checked = st.session_state.get(_task_key(paper_id, index), False)
        task_lines.append(f"- [{'x' if checked else ' '}] {task}")

    score_lines = "\n".join(f"- {name}：{value}/5" for name, value in scores.items())
    note_lines = "\n".join(f"## {name}\n\n{value or '暂无'}" for name, value in notes.items())
    return f"""# 论文学习卡片

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 基本信息

- 标题：{paper.get("title", "Untitled Paper")}
- DOI：{paper.get("doi") or "暂无"}
- 分类：{paper.get("category") or "未分类"}

## 掌握度

{score_lines}

## 复习任务

{chr(10).join(task_lines)}

{note_lines}

## AI 学习包

{pack or "暂无"}
"""


model_name = get_chat_model_label()
page_header(
    "学习中心",
    "把论文从“读过”推进到“能复述、能自测、能复习”的学习工作台。",
    stats=[
        ("Chat 模型", model_name),
        ("学习包", "可生成"),
        ("笔记", "Markdown"),
    ],
)

panel_title("当前对象", "选择要学习的论文")
with st.container(border=True):
    paper = _select_paper()
if paper is None:
    st.stop()

pdf_path = resolve_paper_path(paper)
if not pdf_path.exists():
    st.error("PDF 文件不存在，请回到文献库检查。")
    st.stop()

paper_text = _cached_pdf_text(str(pdf_path), pdf_path.stat().st_mtime)
paper_id = paper["id"]
pack_key = _pack_key(paper_id)
st.session_state.setdefault(pack_key, "")

left, right = st.columns([0.43, 0.57], gap="large")

with left:
    with st.container(border=True):
        paper_identity(paper)
        word_count = len(paper_text.replace("\n", " ").split())
        st.markdown(
            f'<span class="pa-pill">约 {word_count:,} 词</span>'
            f'<span class="pa-pill">模型：{html.escape(model_name)}</span>',
            unsafe_allow_html=True,
        )

    panel_title("掌握度", "1 = 刚开始，5 = 可讲给别人")
    with st.container(border=True):
        scores = []
        scores.append(
            st.slider("术语掌握", 0, 5, 0, key=_score_key(paper_id, "terms"))
        )
        scores.append(
            st.slider("方法复述", 0, 5, 0, key=_score_key(paper_id, "method"))
        )
        scores.append(
            st.slider("实验理解", 0, 5, 0, key=_score_key(paper_id, "experiment"))
        )
        average = sum(scores) / len(scores)
        st.markdown(
            f"""
            <div class="pa-score-band">
                <div class="pa-score-item">
                    <div class="pa-score-label">平均掌握度</div>
                    <div class="pa-score-value">{average:.1f}/5</div>
                </div>
                <div class="pa-score-item">
                    <div class="pa-score-label">已完成任务</div>
                    <div class="pa-score-value">{sum(bool(st.session_state.get(_task_key(paper_id, i))) for i in range(4))}/4</div>
                </div>
                <div class="pa-score-item">
                    <div class="pa-score-label">学习包</div>
                    <div class="pa-score-value">{'已生成' if st.session_state[pack_key] else '未生成'}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    panel_title("复习打卡", "把学习动作拆小")
    review_tasks = [
        "今天：通读摘要、引言和结论，并写下一句话总结",
        "明天：复述方法流程，补齐术语表中不熟的概念",
        "3 天后：不看原文回答自测题，并标记错题",
        "7 天后：用 5 分钟讲清论文贡献、局限和可复现实验",
    ]
    with st.container(border=True):
        for index, task in enumerate(review_tasks):
            st.checkbox(task, key=_task_key(paper_id, index))

with right:
    panel_title("AI 学习包", "学习路线、术语表、自测题、复习计划")
    with st.container(border=True):
        st.markdown(
            """
            <div class="pa-learning-grid">
                <div class="pa-learning-card"><strong>学习路线</strong><span>按阅读顺序拆出目标、重点和耗时。</span></div>
                <div class="pa-learning-card"><strong>术语表</strong><span>解释术语作用，并提醒常见误解。</span></div>
                <div class="pa-learning-card"><strong>方法拆解</strong><span>把输入、模块、流程和输出讲清楚。</span></div>
                <div class="pa-learning-card"><strong>自测题</strong><span>附参考答案，方便主动回忆。</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        action_cols = st.columns([0.42, 0.28, 0.3], gap="small")
        with action_cols[0]:
            generate = st.button(
                "生成学习包",
                type="primary",
                use_container_width=True,
                disabled=not is_configured(),
                key=f"generate_learning_{paper_id}",
            )
        with action_cols[1]:
            if st.button("清空", use_container_width=True, key=f"clear_learning_{paper_id}"):
                st.session_state[pack_key] = ""
                st.rerun()
        with action_cols[2]:
            save_clicked = st.button(
                "保存学习卡片",
                use_container_width=True,
                key=f"save_learning_{paper_id}",
            )

        if not is_configured():
            st.warning("未配置 CHAT_API_KEY 或 DEEPSEEK_API_KEY，暂不能生成 AI 学习包。")

        if generate:
            try:
                with st.status(f"{model_name} 正在生成学习包...", expanded=True) as status:
                    status.write("抽取论文结构和关键概念...")
                    status.write("组织学习路线与自测题...")
                    st.session_state[pack_key] = st.write_stream(
                        stream_learning_pack(paper, paper_text)
                    )
                    status.update(label="学习包生成完成", state="complete")
                st.rerun()
            except Exception as exc:
                st.error(f"学习包生成失败：{exc}")

        if save_clicked:
            content = _build_learning_note(paper, st.session_state[pack_key], review_tasks)
            saved = save_note_raw(
                title=f"{paper.get('title', 'Untitled Paper')} 学习卡片 {datetime.now():%Y%m%d_%H%M%S}",
                content=content,
                category="论文学习卡片",
            )
            st.toast(f"学习卡片已保存至 {saved['path']}")

    tab_pack, tab_notes, tab_source = st.tabs(["学习包", "我的复述", "原文摘取"])
    with tab_pack:
        with st.container(height=640, border=True):
            if st.session_state[pack_key]:
                st.markdown(st.session_state[pack_key])
            else:
                st.markdown(
                    '<div class="pa-empty">点击“生成学习包”后，这里会出现学习路线、术语表、方法拆解、自测题和复习计划。</div>',
                    unsafe_allow_html=True,
                )

    with tab_notes:
        with st.container(border=True):
            st.text_area(
                "一句话总结",
                key=_note_key(paper_id, "one_sentence"),
                height=80,
                placeholder="用一句话讲清这篇论文解决了什么问题。",
            )
            st.text_area(
                "最不懂的问题",
                key=_note_key(paper_id, "hardest"),
                height=90,
                placeholder="记录仍然卡住的概念、公式、实验或假设。",
            )
            st.text_area(
                "可复述的创新点",
                key=_note_key(paper_id, "innovation"),
                height=110,
                placeholder="尝试不看原文复述 1-3 个创新点。",
            )
            st.text_area(
                "下一步行动",
                key=_note_key(paper_id, "next_action"),
                height=90,
                placeholder="例如复现实验、查相关工作、补数学背景。",
            )

    with tab_source:
        with st.container(height=640, border=True):
            st.text_area(
                "论文原文摘取",
                value=paper_text[:40000],
                height=600,
                disabled=True,
                label_visibility="collapsed",
            )
