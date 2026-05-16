"""Markdown study-note generation and persistence."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .agent_tools import save_note_raw
from .llm_client import generate_study_summary, is_configured
from .pdf_utils import annotations_to_markdown


NOTE_CATEGORY = "论文精读笔记"


def _message_lines(history: list[dict[str, str]]) -> str:
    if not history:
        return "暂无"
    lines = []
    for item in history:
        role = "用户" if item.get("role") == "user" else "AI"
        content = item.get("content", "").strip() or "暂无内容"
        lines.append(f"**{role}**：\n\n{content}")
    return "\n\n".join(lines)


def _detail_records_to_markdown(detail_records: dict[str, Any]) -> str:
    if not detail_records:
        return "暂无"

    lines: list[str] = []
    for key in sorted(detail_records, key=lambda item: int(item) if item.isdigit() else 0):
        record = detail_records[key]
        index = int(key) + 1 if key.isdigit() else record.get("paragraph_index", key)
        lines.append(f"### 段落 {index}")
        lines.append("")
        lines.append("**原文**")
        lines.append("")
        lines.append(record.get("original", "暂无"))
        lines.append("")
        explanation = record.get("explanation") or "暂无解释"
        lines.append("**AI 解释**")
        lines.append("")
        lines.append(explanation)
        qas = record.get("qas") or []
        if qas:
            lines.append("")
            lines.append("**围绕本段的问答**")
            lines.append("")
            for qa_index, qa in enumerate(qas, start=1):
                lines.append(f"{qa_index}. 问：{qa.get('question', '')}")
                lines.append(f"   答：{qa.get('answer', '')}")
        lines.append("")
    return "\n".join(lines).strip()


def _confusions_to_markdown(confusions: list[dict[str, str]]) -> str:
    if not confusions:
        return "暂无"
    lines = []
    for index, item in enumerate(confusions, start=1):
        lines.append(f"{index}. **不懂的地方**：{item.get('confusion', '')}")
        lines.append(f"   **AI 补充解释**：{item.get('answer', '')}")
    return "\n".join(lines)


def build_summary_source(
    *,
    paper: dict[str, Any],
    macro_history: list[dict[str, str]],
    detail_records: dict[str, Any],
    detail_history: list[dict[str, str]],
    confusions: list[dict[str, str]],
    custom_note: str,
    pdf_path: str | Path | None,
) -> str:
    """Build a deterministic Markdown source from all local reading data."""

    annotation_md = annotations_to_markdown(pdf_path) if pdf_path else "暂无批注。"
    user_note = custom_note.strip() if custom_note.strip() else "暂无"
    return f"""# 论文精读笔记

## 基本信息

- 论文标题：{paper.get("title", "Untitled Paper")}
- DOI：{paper.get("doi") or "暂无"}
- 分类：{paper.get("category") or "未分类"}
- PDF 文件：{paper.get("filename") or "暂无"}
- 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 宏观解读

{_message_lines(macro_history)}

## 逐段精读记录

{_detail_records_to_markdown(detail_records)}

## 逐段精读对话补充

{_message_lines(detail_history)}

## 我不懂的地方与补充解释

{_confusions_to_markdown(confusions)}

## PDF 高亮与批注

{annotation_md}

## 用户自定义笔记

{user_note}

### 来自 PDF 批注

{annotation_md}
"""


def export_study_note(
    *,
    paper: dict[str, Any],
    macro_history: list[dict[str, str]],
    detail_records: dict[str, Any],
    detail_history: list[dict[str, str]],
    confusions: list[dict[str, str]],
    custom_note: str,
    pdf_path: str | Path | None,
    use_llm: bool = True,
) -> dict[str, Any]:
    """Generate a Markdown note and save it through ``save_note_raw``."""

    source = build_summary_source(
        paper=paper,
        macro_history=macro_history,
        detail_records=detail_records,
        detail_history=detail_history,
        confusions=confusions,
        custom_note=custom_note,
        pdf_path=pdf_path,
    )

    markdown = source
    llm_error = ""
    if use_llm and is_configured():
        try:
            markdown = generate_study_summary(source)
        except Exception as exc:  # The deterministic source is still valuable.
            llm_error = str(exc)
            markdown = source

    title = f"{paper.get('title', 'Untitled Paper')} 精读笔记 {datetime.now():%Y%m%d_%H%M%S}"
    saved = save_note_raw(title=title, content=markdown, category=NOTE_CATEGORY)
    saved["llm_error"] = llm_error
    saved["used_llm"] = use_llm and is_configured() and not llm_error
    return saved

