"""Paper library page: upload PDFs, DOI/arXiv import, and list papers."""

from __future__ import annotations

import html

import streamlit as st

from core.ui import apply_page_style, page_header, panel_title, sidebar_nav
from core.paper_storage import (
    create_category,
    delete_paper,
    download_pdf_by_doi,
    ensure_directories,
    list_categories,
    list_papers,
    save_uploaded_pdf,
    update_paper_title,
)


st.set_page_config(page_title="文献库", layout="wide")
ensure_directories()
apply_page_style()
sidebar_nav("library")


def _choose_category(prefix: str) -> str:
    """Render an inline category chooser with create-new option."""

    categories = list_categories()
    options = categories + ["+ 新建分类"]
    selected = st.selectbox(
        "分类",
        options,
        key=f"{prefix}_category_select",
        label_visibility="collapsed",
    )
    if selected == "+ 新建分类":
        return st.text_input(
            "新分类名称",
            value="NLP",
            key=f"{prefix}_new_category",
            placeholder="输入新分类名称",
        )
    return selected


paper_count = len(list_papers())
category_count = len(list_categories())
page_header(
    "文献库",
    "集中管理论文入库、分类和当前阅读对象。上传区、DOI 导入区与论文列表保持清晰分层。",
    stats=[
        ("论文", str(paper_count)),
        ("分类", str(category_count)),
        ("存储", "Local"),
    ],
)

upload_col, doi_col = st.columns(2, gap="large")

with upload_col:
    panel_title("本地上传", "PDF 入库")
    with st.container(border=True):
        with st.form("upload_pdf_form", clear_on_submit=False):
            uploaded_file = st.file_uploader("选择 PDF 文件", type=["pdf"])
            title = st.text_input("论文标题（可选，默认使用文件名）")
            doi = st.text_input("DOI（可选）")
            category = _choose_category("upload")
            submitted = st.form_submit_button("保存到文献库", type="primary")

    if submitted:
        if uploaded_file is None:
            st.error("请先选择一个 PDF 文件。")
        else:
            try:
                normalized_category = create_category(category)
                paper = save_uploaded_pdf(
                    uploaded_file,
                    category=normalized_category,
                    title=title or None,
                    doi=doi or None,
                )
                st.session_state["selected_paper_id"] = paper["id"]
                st.toast(f"已入库：{paper['title']}")
                st.rerun()
            except Exception as exc:
                st.error(f"上传失败：{exc}")

with doi_col:
    panel_title("DOI 导入", "arXiv PDF 下载")
    with st.container(border=True):
        with st.form("doi_download_form", clear_on_submit=False):
            doi_value = st.text_input("DOI", placeholder="例如 10.48550/arXiv.1706.03762")
            category = _choose_category("doi")
            download_clicked = st.form_submit_button("查找并下载", type="primary")

    if download_clicked:
        try:
            normalized_category = create_category(category)
            with st.spinner("正在查询 arXiv 并下载 PDF..."):
                paper = download_pdf_by_doi(doi_value, category=normalized_category)
            st.session_state["selected_paper_id"] = paper["id"]
            st.toast(f"已从 arXiv 下载：{paper['title']}")
            st.rerun()
        except Exception as exc:
            st.error(f"下载失败：{exc}")
            st.info("如果 DOI 没有对应的 arXiv 条目，请改用左侧本地上传。")

# ── Paper list ──────────────────────────────────────────────

panel_title("已入库论文", "选择、编辑或删除")

papers = list_papers()

if not papers:
    st.info("📚 当前还没有入库论文，请通过上方表单上传或通过 DOI 下载。")
else:
    # Search and sort
    search_col, sort_col, filter_col = st.columns([0.45, 0.25, 0.3])
    with search_col:
        search_query = st.text_input(
            "搜索论文",
            placeholder="按标题、DOI 或文件名搜索...",
            label_visibility="collapsed",
            key="library_search",
        )
    with sort_col:
        sort_by = st.selectbox(
            "排序",
            ["最近上传", "标题 A-Z", "标题 Z-A"],
            label_visibility="collapsed",
            key="library_sort",
        )
    with filter_col:
        filter_category = st.selectbox(
            "分类筛选",
            ["全部", *list_categories()],
            label_visibility="collapsed",
            key="library_filter",
        )

    # Apply filters
    if filter_category != "全部":
        papers = list_papers(filter_category)

    if search_query:
        q = search_query.lower()
        papers = [
            p for p in papers
            if q in (p.get("title", "") or "").lower()
            or q in (p.get("doi", "") or "").lower()
            or q in (p.get("filename", "") or "").lower()
        ]

    if sort_by == "标题 A-Z":
        papers = sorted(papers, key=lambda p: (p.get("title") or "").lower())
    elif sort_by == "标题 Z-A":
        papers = sorted(papers, key=lambda p: (p.get("title") or "").lower(), reverse=True)

    if not papers:
        st.info("没有匹配的论文，请调整搜索或筛选条件。")
    else:
        # Card grid: 2 columns
        cols_per_row = 2
        for i in range(0, len(papers), cols_per_row):
            row_cols = st.columns(cols_per_row, gap="medium")
            for j in range(cols_per_row):
                idx = i + j
                if idx >= len(papers):
                    break
                paper = papers[idx]
                is_current = st.session_state.get("selected_paper_id") == paper["id"]
                card_class = "pa-card-current" if is_current else ""

                with row_cols[j]:
                    with st.container(border=True):
                        if card_class:
                            st.markdown(
                                f'<div class="{card_class}"></div>',
                                unsafe_allow_html=True,
                            )

                        # Title
                        title_text = html.escape(paper.get("title", "Untitled Paper"))
                        st.markdown(
                            f'<div class="pa-card-title">{title_text}</div>',
                            unsafe_allow_html=True,
                        )

                        # Meta: category + date
                        cat = html.escape(paper.get("category", "未分类"))
                        date_str = (paper.get("uploaded_at") or "")[:10]
                        st.markdown(
                            f'<span class="pa-tag">{cat}</span>'
                            f'<span class="pa-card-date">{html.escape(date_str)}</span>',
                            unsafe_allow_html=True,
                        )

                        if is_current:
                            st.caption("当前论文")

                        # Action buttons
                        btn_col1, btn_col2 = st.columns(2, gap="small")
                        with btn_col1:
                            if is_current:
                                st.button(
                                    "当前论文",
                                    key=f"current_badge_{paper['id']}",
                                    disabled=True,
                                    use_container_width=True,
                                )
                            else:
                                if st.button(
                                    "设为当前",
                                    key=f"select_{paper['id']}",
                                    use_container_width=True,
                                    type="primary",
                                ):
                                    st.session_state["selected_paper_id"] = paper["id"]
                                    st.toast(f"已设为当前论文：{paper.get('title', '')[:40]}")
                                    st.rerun()
                        with btn_col2:
                            delete_key = f"delete_confirm_{paper['id']}"
                            if st.session_state.get(delete_key):
                                confirm_col, cancel_col = st.columns(2, gap="small")
                                with confirm_col:
                                    if st.button(
                                        "确认",
                                        key=f"confirm_delete_{paper['id']}",
                                        use_container_width=True,
                                        type="primary",
                                    ):
                                        delete_paper(paper["id"])
                                        if st.session_state.get("selected_paper_id") == paper["id"]:
                                            st.session_state.pop("selected_paper_id", None)
                                        st.session_state[delete_key] = False
                                        st.toast("已删除论文。")
                                        st.rerun()
                                with cancel_col:
                                    if st.button(
                                        "取消",
                                        key=f"cancel_delete_{paper['id']}",
                                        use_container_width=True,
                                    ):
                                        st.session_state[delete_key] = False
                                        st.rerun()
                            else:
                                if st.button(
                                    "删除",
                                    key=f"delete_btn_{paper['id']}",
                                    use_container_width=True,
                                ):
                                    st.session_state[delete_key] = True
                                    st.rerun()

                        # Edit metadata
                        with st.expander("编辑元数据", expanded=False):
                            new_title = st.text_input(
                                "显示标题",
                                value=paper.get("title", ""),
                                key=f"title_{paper['id']}",
                                label_visibility="collapsed",
                                placeholder="论文标题",
                            )
                            if st.button(
                                "保存标题",
                                key=f"save_title_{paper['id']}",
                                use_container_width=True,
                            ):
                                update_paper_title(paper["id"], new_title)
                                st.toast("标题已更新。")
                                st.rerun()
                            st.caption(
                                f"DOI：{paper.get('doi') or '暂无'} | "
                                f"来源：{paper.get('source') or 'upload'}"
                            )
