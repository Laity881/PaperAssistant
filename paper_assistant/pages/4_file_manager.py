"""Local file and category manager for local papers and notes."""

from __future__ import annotations

import html

import streamlit as st

from core.ui import apply_page_style, page_header, panel_title, sidebar_nav
from core.agent_tools import (
    create_category_raw,
    delete_file_raw,
    list_categories_raw,
    list_files_raw,
    move_file_raw,
    read_note_raw,
    rename_file_raw,
)
from core.paper_storage import (
    create_category,
    delete_paper,
    ensure_directories,
    list_categories,
    list_papers,
    move_paper_to_category,
    rename_paper_file,
)


st.set_page_config(page_title="文件管理", layout="wide")
ensure_directories()
apply_page_style()
sidebar_nav("files")


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


page_header(
    "文件管理",
    "直接管理本地 论文/ 与 笔记/ 文件，适合整理分类、清理副本和预览 Markdown 笔记。",
)

paper_tab, note_tab = st.tabs(["📄 论文", "📝 笔记"])

with paper_tab:
    panel_title("论文文件", "论文/")

    with st.expander("+ 创建新分类", expanded=False):
        with st.form("create_paper_category"):
            new_category = st.text_input("分类名称", placeholder="例如 CV / NLP / RL")
            if st.form_submit_button("创建分类", type="primary"):
                if new_category.strip():
                    created = create_category(new_category)
                    st.toast(f"已创建分类：{created}")
                    st.rerun()

    paper_categories = ["全部", *list_categories()]
    selected_category = st.selectbox(
        "按分类筛选论文",
        paper_categories,
        key="paper_file_filter",
    )
    registered_papers = list_papers(selected_category)
    registered_by_path = {paper.get("path"): paper for paper in registered_papers}
    raw_files = list_files_raw(
        "论文",
        category=None if selected_category == "全部" else selected_category,
        suffixes=(".pdf",),
    )

    if not raw_files:
        st.info("没有找到 PDF 文件。")

    for file_info in raw_files:
        paper = registered_by_path.get(file_info["path"])
        is_registered = paper is not None
        status_class = "pa-file-registered" if is_registered else "pa-file-unregistered"
        status_text = "已注册" if is_registered else "未注册"
        status_color = "var(--pa-accent)" if is_registered else "var(--pa-warm)"

        display_title = paper.get("title") if paper else file_info["filename"]

        with st.container(border=True):
            st.markdown(
                f'<div class="{status_class}">'
                f'<strong>{html.escape(display_title)}</strong>'
                f'<span class="pa-file-status" style="color:{status_color}">{status_text}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f"分类：{file_info.get('category') or '未分类'} | "
                f"大小：{_format_size(file_info['size'])} | "
                f"更新时间：{file_info['updated_at']}"
            )
            cols = st.columns([0.34, 0.26, 0.2, 0.2], vertical_alignment="bottom")
            with cols[0]:
                new_name = st.text_input(
                    "重命名文件",
                    value=file_info["filename"],
                    key=f"rename_paper_{file_info['path']}",
                    label_visibility="collapsed",
                )
            with cols[1]:
                target_category = st.selectbox(
                    "移动到分类",
                    list_categories(),
                    key=f"move_paper_{file_info['path']}",
                    label_visibility="collapsed",
                )
            with cols[2]:
                if st.button(
                    "保存修改",
                    key=f"save_paper_file_{file_info['path']}",
                    use_container_width=True,
                ):
                    try:
                        if paper:
                            if new_name != file_info["filename"]:
                                rename_paper_file(paper["id"], new_name)
                            if target_category != paper.get("category"):
                                move_paper_to_category(paper["id"], target_category)
                        else:
                            current_path = file_info["path"]
                            if new_name != file_info["filename"]:
                                renamed = rename_file_raw(current_path, new_name, "论文")
                                current_path = renamed["path"]
                            if target_category != file_info.get("category"):
                                move_file_raw(
                                    current_path,
                                    root_name="论文",
                                    category=target_category,
                                )
                        st.toast("已保存修改。")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"保存失败：{exc}")
            with cols[3]:
                delete_key = f"confirm_paper_file_{file_info['path']}"
                if st.session_state.get(delete_key):
                    confirm_col, cancel_col = st.columns(2, gap="small")
                    with confirm_col:
                        if st.button(
                            "确认",
                            key=f"do_delete_paper_{file_info['path']}",
                            use_container_width=True,
                            type="primary",
                        ):
                            try:
                                if paper:
                                    delete_paper(paper["id"])
                                else:
                                    delete_file_raw(file_info["path"], "论文")
                                st.session_state[delete_key] = False
                                st.toast("已删除。")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"删除失败：{exc}")
                    with cancel_col:
                        if st.button(
                            "取消",
                            key=f"cancel_delete_paper_{file_info['path']}",
                            use_container_width=True,
                        ):
                            st.session_state[delete_key] = False
                            st.rerun()
                else:
                    if st.button(
                        "删除",
                        key=f"delete_paper_file_{file_info['path']}",
                        use_container_width=True,
                    ):
                        st.session_state[delete_key] = True
                        st.rerun()

with note_tab:
    panel_title("笔记文件", "笔记/")

    with st.expander("+ 创建新分类", expanded=False):
        with st.form("create_note_category"):
            new_note_category = st.text_input(
                "分类名称",
                value="论文精读笔记",
                label_visibility="collapsed",
            )
            if st.form_submit_button("创建分类", type="primary"):
                if new_note_category.strip():
                    result = create_category_raw("笔记", new_note_category)
                    st.toast(f"已创建分类：{result['category']}")
                    st.rerun()

    note_categories = ["全部", *list_categories_raw("笔记")]
    selected_note_category = st.selectbox(
        "按分类筛选笔记",
        note_categories,
        key="note_file_filter",
    )
    note_files = list_files_raw(
        "笔记",
        category=None if selected_note_category == "全部" else selected_note_category,
    )

    if not note_files:
        st.info("没有找到笔记文件。")

    for file_info in note_files:
        with st.container(border=True):
            st.markdown(f"**{html.escape(file_info['filename'])}**")
            st.caption(
                f"分类：{file_info.get('category') or '未分类'} | "
                f"大小：{_format_size(file_info['size'])} | "
                f"更新时间：{file_info['updated_at']}"
            )
            cols = st.columns([0.34, 0.26, 0.2, 0.2], vertical_alignment="bottom")
            with cols[0]:
                new_name = st.text_input(
                    "重命名文件",
                    value=file_info["filename"],
                    key=f"rename_note_{file_info['path']}",
                    label_visibility="collapsed",
                )
            with cols[1]:
                target_category = st.selectbox(
                    "移动到分类",
                    list_categories_raw("笔记") or ["论文精读笔记"],
                    key=f"move_note_{file_info['path']}",
                    label_visibility="collapsed",
                )
            with cols[2]:
                if st.button(
                    "保存修改",
                    key=f"save_note_file_{file_info['path']}",
                    use_container_width=True,
                ):
                    try:
                        current_path = file_info["path"]
                        if new_name != file_info["filename"]:
                            renamed = rename_file_raw(current_path, new_name, "笔记")
                            current_path = renamed["path"]
                        if target_category != file_info.get("category"):
                            move_file_raw(
                                current_path,
                                root_name="笔记",
                                category=target_category,
                            )
                        st.toast("已保存修改。")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"保存失败：{exc}")
            with cols[3]:
                delete_key = f"confirm_note_file_{file_info['path']}"
                if st.session_state.get(delete_key):
                    confirm_col, cancel_col = st.columns(2, gap="small")
                    with confirm_col:
                        if st.button(
                            "确认",
                            key=f"do_delete_note_{file_info['path']}",
                            use_container_width=True,
                            type="primary",
                        ):
                            try:
                                delete_file_raw(file_info["path"], "笔记")
                                st.session_state[delete_key] = False
                                st.toast("已删除。")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"删除失败：{exc}")
                    with cancel_col:
                        if st.button(
                            "取消",
                            key=f"cancel_delete_note_{file_info['path']}",
                            use_container_width=True,
                        ):
                            st.session_state[delete_key] = False
                            st.rerun()
                else:
                    if st.button(
                        "删除",
                        key=f"delete_note_file_{file_info['path']}",
                        use_container_width=True,
                    ):
                        st.session_state[delete_key] = True
                        st.rerun()

            if file_info["filename"].lower().endswith(".md"):
                with st.expander("预览", expanded=False):
                    try:
                        note = read_note_raw(file_info["path"])
                        with st.container(height=400, border=True):
                            st.markdown(note["content"])
                    except Exception as exc:
                        st.error(f"读取失败：{exc}")
