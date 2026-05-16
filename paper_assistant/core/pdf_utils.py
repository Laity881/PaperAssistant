"""PDF extraction, paragraph segmentation, viewer fallback, and annotations."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .paper_storage import ANNOTATIONS_DIR


SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?\.])\s+(?=[A-Z0-9\[\(一-龥])")
PAGE_MARK_RE = re.compile(r"^\s*\[Page\s+\d+\]\s*$", re.IGNORECASE)
SECTION_HEADING_RE = re.compile(
    r"^\s*((\d+(\.\d+)*\.?)|([IVX]+\.?)|([A-Z]))\s+[-A-Za-z一-龥].{0,90}$"
)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract full text from a PDF with page markers.

    Page markers are kept only as rough context for the model.  The paragraph
    splitter below removes them before segmentation so one PDF page will not be
    treated as one reading paragraph.
    """

    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("缺少 pdfplumber 依赖，请先安装 requirements.txt。") from exc

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF 不存在：{path}")

    pages: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            if text.strip():
                pages.append(f"\n\n[Page {index}]\n{text.strip()}")
    return "\n".join(pages).strip()


def _remove_page_markers(text: str) -> str:
    """Remove generated page markers while preserving paragraph boundaries."""

    lines = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if PAGE_MARK_RE.match(line):
            lines.append("")
            continue
        lines.append(line)
    return "\n".join(lines)


def _clean_block(text: str) -> str:
    """Normalize one extracted text block."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?<![。！？.!?:：])\n(?!\n)", " ", text)
    return text.strip()


def _looks_like_heading(block: str) -> bool:
    """Return whether a block resembles a section heading."""

    compact = re.sub(r"\s+", " ", block).strip()
    if not compact or len(compact) > 120:
        return False
    if compact.endswith((".", "。", "?", "？", "!", "！")):
        return False
    heading_words = {
        "abstract",
        "introduction",
        "related work",
        "method",
        "methods",
        "experiments",
        "results",
        "conclusion",
        "references",
    }
    return compact.lower() in heading_words or bool(SECTION_HEADING_RE.match(compact))


def _sentences_from_block(block: str) -> list[str]:
    """Split a long block into sentence-like units."""

    block = re.sub(r"\s+", " ", block).strip()
    if not block:
        return []

    sentences = [item.strip() for item in SENTENCE_SPLIT_RE.split(block) if item.strip()]
    if len(sentences) <= 1 and len(block) > 900:
        # Some PDFs lose punctuation spaces.  This fallback cuts at punctuation
        # while still keeping the punctuation with the previous sentence.
        sentences = []
        start = 0
        for match in re.finditer(r"[。！？!?\.]", block):
            end = match.end()
            if end - start >= 120:
                sentences.append(block[start:end].strip())
                start = end
        if start < len(block):
            sentences.append(block[start:].strip())
    return sentences or [block]


def _group_sentences(
    sentences: list[str],
    *,
    min_chars: int,
    max_chars: int,
) -> list[str]:
    """Group sentence units into semantic reading paragraphs."""

    paragraphs: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        if current and current_len + sentence_len > max_chars:
            paragraphs.append(" ".join(current).strip())
            current = []
            current_len = 0

        current.append(sentence)
        current_len += sentence_len

        if current_len >= min_chars:
            paragraphs.append(" ".join(current).strip())
            current = []
            current_len = 0

    if current:
        paragraphs.append(" ".join(current).strip())
    return paragraphs


def split_text_to_paragraphs(
    text: str,
    *,
    min_chars: int = 420,
    max_chars: int = 980,
) -> list[str]:
    """Split extracted PDF text into paragraph-sized reading chunks.

    The previous implementation could turn each PDF page into one paragraph
    because page markers created large blank-line blocks.  This version removes
    page markers first, keeps real blank-line paragraphs when available, and
    splits any overlong block by sentences.  The result is closer to readable
    academic paragraphs even when the PDF extractor loses layout.
    """

    if not text.strip():
        return []

    text = _remove_page_markers(text)
    raw_blocks = [
        _clean_block(block)
        for block in re.split(r"\n\s*\n+", text)
        if _clean_block(block)
    ]

    paragraphs: list[str] = []
    sentence_buffer: list[str] = []

    def flush_buffer() -> None:
        nonlocal sentence_buffer
        if sentence_buffer:
            paragraphs.extend(
                _group_sentences(
                    sentence_buffer,
                    min_chars=min_chars,
                    max_chars=max_chars,
                )
            )
            sentence_buffer = []

    for block in raw_blocks:
        if len(block) < 35:
            continue

        if _looks_like_heading(block):
            flush_buffer()
            paragraphs.append(block)
            continue

        if len(block) <= max_chars:
            if len(block) >= min_chars:
                flush_buffer()
                paragraphs.append(block)
            else:
                sentence_buffer.extend(_sentences_from_block(block))
            continue

        sentence_buffer.extend(_sentences_from_block(block))
        if sum(len(sentence) for sentence in sentence_buffer) >= max_chars:
            flush_buffer()

    flush_buffer()
    return [paragraph for paragraph in paragraphs if len(paragraph.strip()) >= 20]


def extract_paragraphs_from_pdf(pdf_path: str | Path) -> list[str]:
    """Extract and split a PDF into reading paragraphs."""

    return split_text_to_paragraphs(extract_text_from_pdf(pdf_path))


def render_pdf_viewer(pdf_path: str | Path, *, height: int = 620) -> bool:
    """Render a PDF in Streamlit if ``streamlit-pdf-viewer`` is installed."""

    import streamlit as st

    display_path = preferred_pdf_for_reading(pdf_path)
    try:
        from streamlit_pdf_viewer import pdf_viewer
    except ImportError:
        st.info("未安装 streamlit-pdf-viewer，已切换为文本阅读模式。")
        return False

    try:
        try:
            pdf_viewer(input=str(display_path), height=height, render_text=True)
        except TypeError:
            pdf_viewer(str(display_path), height=height)
        return True
    except Exception as exc:  # pragma: no cover - depends on browser component
        st.warning(f"PDF 阅读器加载失败，已切换为文本模式：{exc}")
        return False


def preferred_pdf_for_reading(pdf_path: str | Path) -> Path:
    """Use the annotated PDF copy when one exists."""

    path = Path(pdf_path)
    annotated = path.with_name(f"{path.stem}_annotated.pdf")
    return annotated if annotated.exists() else path


def annotation_file_for_pdf(pdf_path: str | Path) -> Path:
    """Return the JSON annotation path for a PDF."""

    ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = Path(pdf_path)
    return ANNOTATIONS_DIR / f"{path.stem}.annotations.json"


def load_annotations(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Load locally saved highlight/comment data."""

    path = annotation_file_for_pdf(pdf_path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def save_annotations(pdf_path: str | Path, annotations: list[dict[str, Any]]) -> None:
    """Persist annotation JSON."""

    path = annotation_file_for_pdf(pdf_path)
    path.write_text(
        json.dumps(annotations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _hex_to_rgb(color: str) -> tuple[float, float, float]:
    color = (color or "#fff176").strip().lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", color):
        color = "fff176"
    return (
        int(color[0:2], 16) / 255,
        int(color[2:4], 16) / 255,
        int(color[4:6], 16) / 255,
    )


def _search_candidates(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    candidates = [normalized]
    if len(normalized) > 180:
        candidates.append(normalized[:180])
    if len(normalized) > 80:
        candidates.append(normalized[:80])
    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def rebuild_annotated_pdf(pdf_path: str | Path) -> Path:
    """Regenerate the annotated PDF copy from the original PDF and JSON data."""

    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("缺少 pymupdf 依赖，请先安装 requirements.txt。") from exc

    source = Path(pdf_path)
    annotations = load_annotations(source)
    output = source.with_name(f"{source.stem}_annotated.pdf")

    doc = fitz.open(str(source))
    for annotation in annotations:
        target_text = (annotation.get("target_text") or "").strip()
        if not target_text:
            annotation["status"] = "empty_target"
            continue

        page_number = annotation.get("page_number")
        if isinstance(page_number, int) and 1 <= page_number <= len(doc):
            page_indexes = [page_number - 1]
        else:
            page_indexes = list(range(len(doc)))

        found = False
        for page_index in page_indexes:
            page = doc[page_index]
            rects = []
            for candidate in _search_candidates(target_text):
                rects = page.search_for(candidate)
                if rects:
                    break
            if not rects:
                continue

            color = _hex_to_rgb(annotation.get("color", "#fff176"))
            highlight = page.add_highlight_annot(rects)
            highlight.set_colors(stroke=color)
            note = annotation.get("note", "")
            if note:
                highlight.set_info(content=note)
            highlight.update()

            if note:
                page.add_text_annot(rects[0].br, note)

            annotation["status"] = "applied"
            annotation["page_number"] = page_index + 1
            found = True
            break

        if not found:
            annotation["status"] = "not_found"

    if output.exists():
        output.unlink()
    doc.save(str(output), garbage=4, deflate=True)
    doc.close()
    save_annotations(source, annotations)
    return output


def add_annotation(
    pdf_path: str | Path,
    *,
    target_text: str,
    note: str = "",
    color: str = "#fff176",
    kind: str = "highlight",
) -> dict[str, Any]:
    """Store a highlight/comment and regenerate the annotated PDF copy."""

    target_text = (target_text or "").strip()
    if not target_text:
        raise ValueError("请先填写要高亮或批注的原文片段。")

    annotation = {
        "id": uuid.uuid4().hex,
        "kind": kind,
        "target_text": target_text,
        "note": note.strip(),
        "color": color,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
    }
    annotations = load_annotations(pdf_path)
    annotations.append(annotation)
    save_annotations(pdf_path, annotations)
    rebuild_annotated_pdf(pdf_path)
    return annotation


def delete_annotation(pdf_path: str | Path, annotation_id: str) -> bool:
    """Delete an annotation by id and rebuild the annotated PDF."""

    annotations = load_annotations(pdf_path)
    updated = [item for item in annotations if item.get("id") != annotation_id]
    if len(updated) == len(annotations):
        return False
    save_annotations(pdf_path, updated)
    rebuild_annotated_pdf(pdf_path)
    return True


def annotations_to_markdown(pdf_path: str | Path) -> str:
    """Format annotations as Markdown for the study note."""

    annotations = load_annotations(pdf_path)
    if not annotations:
        return "暂无批注。"

    lines: list[str] = []
    for index, item in enumerate(annotations, start=1):
        target = item.get("target_text", "").strip()
        note = item.get("note", "").strip()
        page = item.get("page_number") or "未知页"
        status = item.get("status", "")
        lines.append(f"{index}. 页码：{page}；状态：{status}")
        lines.append(f"   - 原文：{target}")
        if note:
            lines.append(f"   - 批注：{note}")
    return "\n".join(lines)

