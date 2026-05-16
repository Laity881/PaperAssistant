"""Detail reading page: section-level explanation, QA, and annotations."""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from core.llm_client import (
    get_chat_model_label,
    is_configured,
    stream_answer_detail_question,
    stream_explain_confusion,
    stream_explain_paragraph,
)
from core.note_exporter import export_study_note
from core.paper_storage import (
    ensure_directories,
    get_paper_by_id,
    list_papers,
    resolve_paper_path,
)
from core.pdf_utils import (
    add_annotation,
    delete_annotation,
    extract_text_from_pdf,
    load_annotations,
    render_pdf_viewer,
    split_text_to_sections,
)
from core.ui import (
    READING_PANEL_HEIGHT,
    apply_page_style,
    page_header,
    panel_title,
    paper_identity,
    sidebar_nav,
)


st.set_page_config(page_title="逐章节精读", layout="wide")
ensure_directories()
apply_page_style()
sidebar_nav("detail")
MODEL_NAME = get_chat_model_label()


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
        key="detail_paper_search",
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


def _keys(paper_id: str) -> dict[str, str]:
    return {
        "current": f"current_section_{paper_id}",
        "records": f"detail_records_{paper_id}",
        "history": f"detail_history_{paper_id}",
        "confusions": f"confusions_{paper_id}",
        "custom": f"custom_note_{paper_id}",
        "auto": f"auto_explain_{paper_id}",
    }


def _ensure_state(keys: dict[str, str]) -> None:
    st.session_state.setdefault(keys["current"], 0)
    st.session_state.setdefault(keys["records"], {})
    st.session_state.setdefault(keys["history"], [])
    st.session_state.setdefault(keys["confusions"], [])
    st.session_state.setdefault(keys["auto"], True)


def _save_record(
    keys: dict[str, str],
    index: int,
    section: str,
    explanation: str,
) -> None:
    records = st.session_state[keys["records"]]
    records[str(index)] = {
        "section_index": index,
        "original": section,
        "explanation": explanation,
        "qas": records.get(str(index), {}).get("qas", []),
    }


def _run_explanation_if_needed(
    *,
    keys: dict[str, str],
    sections: list[str],
    paper_text: str,
    current_index: int,
    force: bool = False,
    render: bool = True,
) -> None:
    record_key = str(current_index)
    records = st.session_state[keys["records"]]
    if not force and record_key in records:
        return
    if not is_configured():
        st.warning("未配置 CHAT_API_KEY 或 DEEPSEEK_API_KEY，暂不能自动解释章节。")
        return

    with st.spinner(f"正在精读第 {current_index + 1} 个章节片段..."):
        stream = stream_explain_paragraph(
            sections[current_index],
            paper_text,
            paragraph_index=current_index,
            total_paragraphs=len(sections),
        )
        explanation = st.write_stream(stream) if render else "".join(stream)
    _save_record(keys, current_index, sections[current_index], explanation)


def _show_chat(history: list[dict[str, str]]) -> None:
    if not history:
        st.markdown(
            '<div class="pa-empty">这里会保存你在逐章节精读中的追问、“下一章”操作和 AI 回答。</div>',
            unsafe_allow_html=True,
        )
        return

    for message in history:
        role = message.get("role", "assistant")
        with st.chat_message(role):
            st.markdown(message.get("content", ""))


def _annotation_panel(pdf_path: Path) -> None:
    with st.expander("PDF 高亮与批注", expanded=False):
        cols = st.columns([0.68, 0.32], gap="large")
        with cols[0]:
            target_text = st.text_area(
                "原文片段",
                key=f"annotation_target_{pdf_path.stem}",
                height=92,
                placeholder="粘贴 PDF 中想高亮或批注的一小段原文",
            )
            note = st.text_area(
                "批注",
                key=f"annotation_note_{pdf_path.stem}",
                height=82,
                placeholder="写下你的理解、疑问或补充",
            )
        with cols[1]:
            color = st.color_picker(
                "高亮颜色",
                "#fff176",
                key=f"annotation_color_{pdf_path.stem}",
            )
            if st.button(
                "添加高亮/批注",
                use_container_width=True,
                key=f"add_annotation_{pdf_path.stem}",
            ):
                try:
                    add_annotation(
                        pdf_path,
                        target_text=target_text,
                        note=note,
                        color=color,
                        kind="highlight",
                    )
                    st.toast("批注已保存，并已生成带批注的 PDF 副本。")
                    st.rerun()
                except Exception as exc:
                    st.error(f"添加批注失败：{exc}")

        annotations = load_annotations(pdf_path)
        if annotations:
            st.write("已保存批注")
        for item in annotations:
            with st.container(border=True):
                st.caption(
                    f"页码：{item.get('page_number', '未知')} | "
                    f"状态：{item.get('status', 'pending')} | "
                    f"{item.get('created_at', '')}"
                )
                st.write(item.get("target_text", ""))
                if item.get("note"):
                    st.markdown(f"**批注**：{item.get('note')}")
                if st.button("删除批注", key=f"delete_annotation_{item.get('id')}"):
                    delete_annotation(pdf_path, item.get("id", ""))
                    st.rerun()


def _export_controls(paper: dict, pdf_path: Path, keys: dict[str, str]) -> None:
    st.text_area(
        "学习笔记（可选）",
        key=keys["custom"],
        height=100,
        placeholder="写一些自己的总结和心得...",
        label_visibility="collapsed",
    )
    if st.button(
        "生成并导出总结",
        type="primary",
        use_container_width=True,
        key=f"export_detail_{paper['id']}",
    ):
        with st.spinner("正在生成 Markdown 总结..."):
            result = export_study_note(
                paper=paper,
                macro_history=st.session_state.get(f"macro_history_{paper['id']}", []),
                detail_records=st.session_state.get(keys["records"], {}),
                detail_history=st.session_state.get(keys["history"], []),
                confusions=st.session_state.get(keys["confusions"], []),
                custom_note=st.session_state.get(keys["custom"], ""),
                pdf_path=pdf_path,
                use_llm=True,
            )
        st.toast(f"总结已保存至 {result['path']}")
        if result.get("llm_error"):
            st.warning(f"AI 整理失败，已保存原始结构化笔记：{result['llm_error']}")


def _navigate(keys: dict[str, str], index: int) -> None:
    st.session_state[keys["current"]] = index
    st.rerun()


page_header(
    "逐章节精读",
    "按论文章节推进阅读，原文、PDF、解释和问答被组织在左右固定高度的精读工作台中。",
)

panel_title("当前对象", "选择要精读的论文")
with st.container(border=True):
    paper = _select_paper()
if paper is None:
    st.stop()

pdf_path = resolve_paper_path(paper)
if not pdf_path.exists():
    st.error("PDF 文件不存在，请回到文献库检查。")
    st.stop()

paper_text = _cached_pdf_text(str(pdf_path), pdf_path.stat().st_mtime)
sections = split_text_to_sections(paper_text)
if not sections:
    st.error("未能从 PDF 中提取可读章节。")
    st.stop()

keys = _keys(paper["id"])
_ensure_state(keys)
current_index = min(st.session_state[keys["current"]], len(sections) - 1)
st.session_state[keys["current"]] = current_index

left, right = st.columns([0.6, 0.4], gap="large")

with left:
    with st.container(border=True):
        paper_identity(paper)
        st.markdown(
            f"""
            <span class="pa-pill">共 {len(sections)} 个章节片段</span>
            <span class="pa-pill">当前第 {current_index + 1} 章</span>
            """,
            unsafe_allow_html=True,
        )

    panel_title("阅读导航", f"章节 {current_index + 1} / {len(sections)}")
    # Row 1: Prev / Next
    nav_row1 = st.columns([0.5, 0.5], gap="small")
    with nav_row1[0]:
        if st.button(
            "← 上一章",
            use_container_width=True,
            disabled=current_index == 0,
            key="prev_para",
        ):
            _navigate(keys, current_index - 1)
    with nav_row1[1]:
        if st.button(
            "下一章 →",
            use_container_width=True,
            disabled=current_index >= len(sections) - 1,
            key="next_para",
        ):
            _navigate(keys, current_index + 1)

    # Row 2: Jump
    nav_row2 = st.columns([0.65, 0.35], gap="small")
    with nav_row2[0]:
        jump_target = st.number_input(
            "跳转到章节",
            min_value=1,
            max_value=len(sections),
            value=current_index + 1,
            step=1,
            label_visibility="collapsed",
            key="jump_number",
        )
    with nav_row2[1]:
        if st.button("跳转", use_container_width=True, key="jump_btn"):
            _navigate(keys, int(jump_target) - 1)

    tab_text, tab_pdf, tab_list = st.tabs(["当前章节", "PDF", "章节列表"])
    with tab_text:
        with st.container(height=READING_PANEL_HEIGHT, border=True):
            st.markdown(
                f"<div class='selected-para'>{html.escape(sections[current_index])}</div>",
                unsafe_allow_html=True,
            )
    with tab_pdf:
        with st.container(height=READING_PANEL_HEIGHT, border=True):
            rendered = render_pdf_viewer(pdf_path, height=READING_PANEL_HEIGHT - 34)
            if not rendered:
                st.text_area(
                    "论文文本",
                    value=paper_text[:30000],
                    height=READING_PANEL_HEIGHT - 70,
                    disabled=True,
                    label_visibility="collapsed",
                )
    with tab_list:
        with st.container(height=READING_PANEL_HEIGHT, border=True):
            # Quick-jump selectbox
            para_options = [
                f"章节 {i + 1}: {p.replace(chr(10), ' ')[:80]}..."
                for i, p in enumerate(sections)
            ]
            quick_jump = st.selectbox(
                "快速跳转",
                options=list(range(len(sections))),
                index=current_index,
                format_func=lambda i: para_options[i],
                key="para_quick_jump",
                label_visibility="collapsed",
            )
            if quick_jump != current_index:
                _navigate(keys, quick_jump)

            st.divider()

            # Visual numbered list
            list_html = '<div class="pa-para-list">'
            for index, section in enumerate(sections):
                excerpt = section.replace("\n", " ")
                excerpt = excerpt[:120] + ("..." if len(excerpt) > 120 else "")
                css_class = (
                    "pa-para-list-item pa-para-current"
                    if index == current_index
                    else "pa-para-list-item"
                )
                list_html += (
                    f'<div class="{css_class}">'
                    f'<span class="pa-para-num">{index + 1}</span>'
                    f'<span class="pa-para-excerpt">{html.escape(excerpt)}</span>'
                    f'</div>'
                )
            list_html += '</div>'
            st.markdown(list_html, unsafe_allow_html=True)

    _annotation_panel(pdf_path)

with right:
    panel_title(f"{MODEL_NAME} 精读工作区", "解释、问答、笔记导出")

    explain_now = st.button(
        "解释当前章节",
        type="primary",
        use_container_width=True,
        key=f"explain_now_{paper['id']}",
    )

    # Secondary row: auto toggle + clear
    ctrl_cols = st.columns([0.5, 0.5], gap="small")
    with ctrl_cols[0]:
        st.toggle("自动解释", key=keys["auto"])
    with ctrl_cols[1]:
        if st.button(
            "清空记录",
            use_container_width=True,
            key=f"clear_detail_{paper['id']}",
        ):
            st.session_state[keys["records"]] = {}
            st.session_state[keys["history"]] = []
            st.session_state[keys["confusions"]] = []
            st.rerun()

    tab_explain, tab_chat, tab_note = st.tabs(["AI 解释", "问答记录", "笔记导出"])

    with tab_explain:
        with st.container(height=READING_PANEL_HEIGHT, border=True):
            if st.session_state[keys["auto"]] or explain_now:
                try:
                    _run_explanation_if_needed(
                        keys=keys,
                        sections=sections,
                        paper_text=paper_text,
                        current_index=current_index,
                        force=explain_now,
                        render=True,
                    )
                    if explain_now:
                        st.rerun()
                except Exception as exc:
                    st.error(f"章节解释失败：{exc}")

            record = st.session_state[keys["records"]].get(str(current_index))
            if record:
                st.markdown(record.get("explanation", ""))
            else:
                st.markdown(
                    '<div class="pa-empty">点击“解释当前章节”，生成原文引用、中文翻译、面向初学者的解释和可能不懂的点。</div>',
                    unsafe_allow_html=True,
                )

    with tab_chat:
        with st.container(height=READING_PANEL_HEIGHT - 150, border=True):
            _show_chat(st.session_state[keys["history"]])

        with st.form(f"confusion_form_{paper['id']}"):
            confusion_cols = st.columns([0.72, 0.28], vertical_alignment="bottom")
            with confusion_cols[0]:
                confusion = st.text_area(
                    "标记我不懂的地方",
                    height=68,
                    label_visibility="collapsed",
                    placeholder="写下你的疑问...",
                )
            with confusion_cols[1]:
                submit_confusion = st.form_submit_button(
                    "获取补充解释",
                    type="primary",
                )
        if submit_confusion and confusion.strip():
            try:
                with st.spinner("正在补充解释..."):
                    answer = st.write_stream(
                        stream_explain_confusion(
                            confusion,
                            paper_text,
                            sections[current_index],
                        )
                    )
                st.session_state[keys["confusions"]].append(
                    {
                        "section_index": str(current_index),
                        "confusion": confusion,
                        "answer": answer,
                    }
                )
                st.session_state[keys["history"]].append(
                    {"role": "user", "content": f"我不懂：{confusion}"}
                )
                st.session_state[keys["history"]].append(
                    {"role": "assistant", "content": answer}
                )
                st.rerun()
            except Exception as exc:
                st.error(f"补充解释失败：{exc}")

    with tab_note:
        with st.container(height=READING_PANEL_HEIGHT, border=True):
            _export_controls(paper, pdf_path, keys)

prompt = st.chat_input('提问，或输入“下一章”自动切换到下一章。')
if prompt:
    st.session_state[keys["history"]].append({"role": "user", "content": prompt})
    normalized = prompt.strip().lower().rstrip("。.!！")
    try:
        if normalized in {"下一章", "下一节", "next"}:
            next_index = min(st.session_state[keys["current"]] + 1, len(sections) - 1)
            st.session_state[keys["current"]] = next_index
            _run_explanation_if_needed(
                keys=keys,
                sections=sections,
                paper_text=paper_text,
                current_index=next_index,
                render=False,
            )
            record = st.session_state[keys["records"]].get(str(next_index), {})
            answer = f"已切换到第 {next_index + 1} 个章节片段。\n\n{record.get('explanation', '')}"
        else:
            selected = sections[st.session_state[keys["current"]]]
            with st.spinner(f"{MODEL_NAME} 正在结合全文和当前章节回答..."):
                with st.chat_message("assistant"):
                    answer = st.write_stream(
                        stream_answer_detail_question(
                            prompt,
                            paper_text,
                            selected,
                            st.session_state[keys["history"]],
                        )
                    )
            record_key = str(st.session_state[keys["current"]])
            records = st.session_state[keys["records"]]
            records.setdefault(
                record_key,
                {
                    "section_index": st.session_state[keys["current"]],
                    "original": selected,
                    "explanation": "",
                    "qas": [],
                },
            )
            records[record_key].setdefault("qas", []).append(
                {"question": prompt, "answer": answer}
            )
        st.session_state[keys["history"]].append({"role": "assistant", "content": answer})
    except Exception as exc:
        st.session_state[keys["history"]].append(
            {
                "role": "assistant",
                "content": f"调用失败：{exc}\n\n请检查 API Key 或稍后重试。",
            }
        )
    st.rerun()
