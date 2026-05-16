"""Local paper storage, metadata, categories, and DOI/arXiv download helpers.

The application stores PDFs under ``论文/<category>/`` and keeps a small
JSON metadata index at ``论文/metadata.json``.  The index makes the UI fast
and keeps user-visible fields such as title, DOI, category, and upload time
separate from the physical file name.
"""

from __future__ import annotations

import json
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
PAPERS_DIR = BASE_DIR / "论文"
NOTES_DIR = BASE_DIR / "笔记"
ANNOTATIONS_DIR = BASE_DIR / "批注"
METADATA_PATH = PAPERS_DIR / "metadata.json"
LEGACY_DIRS = {
    BASE_DIR / "papers": PAPERS_DIR,
    BASE_DIR / "notes": NOTES_DIR,
    BASE_DIR / "annotations": ANNOTATIONS_DIR,
}
LEGACY_PATH_PREFIXES = {
    "papers": "论文",
    "notes": "笔记",
    "annotations": "批注",
}

DEFAULT_CATEGORY = "未分类"
INVALID_FILENAME_CHARS = r'<>:"/\|?*'


def _non_conflicting_path(directory: Path, filename: str) -> Path:
    path = directory / filename
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    counter = 2
    while True:
        candidate = directory / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _merge_directory(source: Path, target: Path) -> None:
    """Move legacy directory contents into the new Chinese directory."""

    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        destination = target / item.name
        if item.is_dir() and destination.exists() and destination.is_dir():
            _merge_directory(item, destination)
            try:
                item.rmdir()
            except OSError:
                pass
            continue

        if destination.exists():
            destination = _non_conflicting_path(target, item.name)
        shutil.move(str(item), str(destination))

    try:
        source.rmdir()
    except OSError:
        pass


def _migrate_legacy_directories() -> None:
    """Migrate old English data folders to Chinese folders."""

    for legacy, target in LEGACY_DIRS.items():
        if not legacy.exists() or legacy.resolve() == target.resolve():
            continue
        if not target.exists():
            legacy.rename(target)
        else:
            _merge_directory(legacy, target)


def _rewrite_legacy_data_path(raw_path: str) -> str:
    path = (raw_path or "").replace("\\", "/")
    for old, new in LEGACY_PATH_PREFIXES.items():
        if path == old:
            return new
        if path.startswith(f"{old}/"):
            return f"{new}/{path[len(old) + 1:]}"
    return raw_path


def _normalize_metadata_paths() -> None:
    """Rewrite metadata paths from legacy English folders to Chinese folders."""

    if not METADATA_PATH.exists():
        return
    try:
        items = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(items, list):
        return

    changed = False
    for paper in items:
        if not isinstance(paper, dict):
            continue
        for key in ("path", "stored_path"):
            if key in paper:
                updated = _rewrite_legacy_data_path(str(paper.get(key) or ""))
                if updated != paper.get(key):
                    paper[key] = updated
                    changed = True
    if changed:
        METADATA_PATH.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def ensure_directories() -> None:
    """Create all local data directories and an empty metadata index."""

    _migrate_legacy_directories()
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)
    if not METADATA_PATH.exists():
        METADATA_PATH.write_text("[]", encoding="utf-8")
    _normalize_metadata_paths()


def safe_filename(name: str, default: str = "untitled") -> str:
    """Return a Windows-safe file or folder name while preserving readability."""

    cleaned = re.sub(f"[{re.escape(INVALID_FILENAME_CHARS)}]+", "_", name or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned[:160] or default


def normalize_category(category: str | None) -> str:
    """Normalize a user-entered category name."""

    return safe_filename((category or DEFAULT_CATEGORY).strip(), DEFAULT_CATEGORY)


def category_path(category: str | None) -> Path:
    """Return the path for a paper category, creating it if necessary."""

    path = PAPERS_DIR / normalize_category(category)
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_categories() -> list[str]:
    """List available paper categories."""

    ensure_directories()
    categories = [
        item.name
        for item in PAPERS_DIR.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    ]
    if DEFAULT_CATEGORY not in categories:
        categories.append(DEFAULT_CATEGORY)
    return sorted(categories, key=str.lower)


def create_category(category: str) -> str:
    """Create a category folder and return the normalized category name."""

    normalized = normalize_category(category)
    category_path(normalized)
    return normalized


def load_metadata() -> list[dict[str, Any]]:
    """Load paper metadata.  A corrupt file is treated as an empty library."""

    ensure_directories()
    try:
        data = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        data = []
    return data if isinstance(data, list) else []


def save_metadata(items: list[dict[str, Any]]) -> None:
    """Persist the metadata index."""

    ensure_directories()
    METADATA_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _relative_to_base(path: Path) -> str:
    return path.resolve().relative_to(BASE_DIR.resolve()).as_posix()


def resolve_paper_path(paper: dict[str, Any]) -> Path:
    """Resolve a metadata record to an absolute PDF path."""

    raw_path = _rewrite_legacy_data_path(paper.get("path") or paper.get("stored_path") or "")
    path = Path(raw_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path.resolve()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _unique_path(directory: Path, filename: str) -> Path:
    """Return a non-existing path by adding ``_2``, ``_3`` ... if needed."""

    filename = safe_filename(filename)
    path = directory / filename
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    counter = 2
    while True:
        candidate = directory / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def guess_title_from_filename(filename: str) -> str:
    """Create a display title from a PDF filename."""

    title = Path(filename).stem.replace("_", " ").replace("-", " ")
    title = re.sub(r"\s+", " ", title).strip()
    return title or "Untitled Paper"


def list_papers(category: str | None = None) -> list[dict[str, Any]]:
    """Return all registered papers, optionally filtered by category."""

    items = load_metadata()
    if category and category != "全部":
        normalized = normalize_category(category)
        items = [paper for paper in items if paper.get("category") == normalized]
    return sorted(items, key=lambda item: item.get("uploaded_at", ""), reverse=True)


def get_paper_by_id(paper_id: str | None) -> dict[str, Any] | None:
    """Find a paper metadata record by id."""

    if not paper_id:
        return None
    for paper in load_metadata():
        if paper.get("id") == paper_id:
            return paper
    return None


def _register_pdf(
    pdf_path: Path,
    *,
    title: str | None = None,
    category: str | None = None,
    doi: str | None = None,
    source: str = "upload",
    arxiv_id: str | None = None,
) -> dict[str, Any]:
    """Add a saved PDF to the metadata index and return the record."""

    paper = {
        "id": uuid.uuid4().hex,
        "title": (title or guess_title_from_filename(pdf_path.name)).strip(),
        "doi": (doi or "").strip(),
        "category": normalize_category(category),
        "filename": pdf_path.name,
        "path": _relative_to_base(pdf_path),
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "arxiv_id": arxiv_id or "",
    }
    items = load_metadata()
    items.append(paper)
    save_metadata(items)
    return paper


def save_uploaded_pdf(
    uploaded_file: Any,
    *,
    category: str | None,
    title: str | None = None,
    doi: str | None = None,
) -> dict[str, Any]:
    """Save a Streamlit uploaded PDF into the selected category."""

    ensure_directories()
    folder = category_path(category)
    original_name = safe_filename(getattr(uploaded_file, "name", "paper.pdf"))
    if not original_name.lower().endswith(".pdf"):
        original_name = f"{Path(original_name).stem}.pdf"
    target = _unique_path(folder, original_name)

    data = uploaded_file.getvalue()
    target.write_bytes(data)
    return _register_pdf(
        target,
        title=title,
        category=category,
        doi=doi,
        source="upload",
    )


def download_pdf_by_doi(doi: str, *, category: str | None) -> dict[str, Any]:
    """Download a PDF from arXiv by DOI and register it.

    The arXiv API supports DOI search for many papers that were cross-listed
    with journal metadata.  If no match is found, the caller should ask the user
    to upload the PDF manually.
    """

    ensure_directories()
    doi = (doi or "").strip()
    if not doi:
        raise ValueError("请输入 DOI。")

    try:
        import arxiv
    except ImportError as exc:
        raise RuntimeError("缺少 arxiv 依赖，请先安装 requirements.txt。") from exc

    client = arxiv.Client()
    queries = [f'doi:"{doi}"', f"doi:{doi}", f'all:"{doi}"']
    result = None
    for query in queries:
        search = arxiv.Search(
            query=query,
            max_results=5,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        for candidate in client.results(search):
            candidate_doi = (getattr(candidate, "doi", "") or "").lower()
            if not candidate_doi or doi.lower() in candidate_doi:
                result = candidate
                break
        if result:
            break

    if result is None:
        raise LookupError("没有在 arXiv 找到与该 DOI 对应的 PDF，请手动上传。")

    folder = category_path(category)
    title = safe_filename(getattr(result, "title", "") or doi, "paper")
    filename = f"{title}.pdf"
    target = _unique_path(folder, filename)
    downloaded_path = result.download_pdf(dirpath=str(folder), filename=target.name)
    pdf_path = Path(downloaded_path)

    return _register_pdf(
        pdf_path,
        title=getattr(result, "title", "") or title,
        category=category,
        doi=getattr(result, "doi", "") or doi,
        source="arxiv",
        arxiv_id=getattr(result, "entry_id", "") or "",
    )


def delete_paper(paper_id: str) -> bool:
    """Delete a paper PDF, its generated annotation copy, and its metadata."""

    items = load_metadata()
    paper = next((item for item in items if item.get("id") == paper_id), None)
    if paper is None:
        return False

    pdf_path = resolve_paper_path(paper)
    if pdf_path.exists() and _is_within(pdf_path, PAPERS_DIR):
        pdf_path.unlink()

    annotated = pdf_path.with_name(f"{pdf_path.stem}_annotated.pdf")
    if annotated.exists() and _is_within(annotated, PAPERS_DIR):
        annotated.unlink()

    annotation_json = ANNOTATIONS_DIR / f"{pdf_path.stem}.annotations.json"
    if annotation_json.exists() and _is_within(annotation_json, ANNOTATIONS_DIR):
        annotation_json.unlink()

    save_metadata([item for item in items if item.get("id") != paper_id])
    return True


def rename_paper_file(paper_id: str, new_filename: str) -> dict[str, Any]:
    """Rename the PDF file for a paper and update metadata."""

    items = load_metadata()
    paper = next((item for item in items if item.get("id") == paper_id), None)
    if paper is None:
        raise KeyError("找不到该论文。")

    old_path = resolve_paper_path(paper)
    if not old_path.exists():
        raise FileNotFoundError("原 PDF 文件不存在。")
    if not _is_within(old_path, PAPERS_DIR):
        raise ValueError("非法文件路径。")

    new_filename = safe_filename(new_filename)
    if not new_filename.lower().endswith(".pdf"):
        new_filename = f"{Path(new_filename).stem}.pdf"
    new_path = _unique_path(old_path.parent, new_filename)
    old_path.rename(new_path)

    old_annotated = old_path.with_name(f"{old_path.stem}_annotated.pdf")
    if old_annotated.exists():
        old_annotated.rename(new_path.with_name(f"{new_path.stem}_annotated.pdf"))

    old_json = ANNOTATIONS_DIR / f"{old_path.stem}.annotations.json"
    if old_json.exists():
        old_json.rename(ANNOTATIONS_DIR / f"{new_path.stem}.annotations.json")

    paper["filename"] = new_path.name
    paper["path"] = _relative_to_base(new_path)
    save_metadata(items)
    return paper


def move_paper_to_category(paper_id: str, new_category: str) -> dict[str, Any]:
    """Move a paper PDF into another category folder."""

    items = load_metadata()
    paper = next((item for item in items if item.get("id") == paper_id), None)
    if paper is None:
        raise KeyError("找不到该论文。")

    old_path = resolve_paper_path(paper)
    if not old_path.exists():
        raise FileNotFoundError("原 PDF 文件不存在。")
    if not _is_within(old_path, PAPERS_DIR):
        raise ValueError("非法文件路径。")

    folder = category_path(new_category)
    new_path = _unique_path(folder, old_path.name)
    shutil.move(str(old_path), str(new_path))

    old_annotated = old_path.with_name(f"{old_path.stem}_annotated.pdf")
    if old_annotated.exists():
        shutil.move(
            str(old_annotated),
            str(new_path.with_name(f"{new_path.stem}_annotated.pdf")),
        )

    paper["category"] = normalize_category(new_category)
    paper["filename"] = new_path.name
    paper["path"] = _relative_to_base(new_path)
    save_metadata(items)
    return paper


def update_paper_title(paper_id: str, new_title: str) -> dict[str, Any]:
    """Update the display title for a paper."""

    items = load_metadata()
    paper = next((item for item in items if item.get("id") == paper_id), None)
    if paper is None:
        raise KeyError("找不到该论文。")
    paper["title"] = (new_title or paper.get("title") or "Untitled Paper").strip()
    save_metadata(items)
    return paper
