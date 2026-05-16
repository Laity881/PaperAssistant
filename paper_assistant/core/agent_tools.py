"""Small local note/file tools inspired by the Gas Station tool style.

The functions are deliberately simple and side-effect explicit.  They operate
under the app's local ``notes/`` and ``papers/`` folders only, so pages can use
them as lightweight backend tools without exposing arbitrary filesystem access.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .paper_storage import BASE_DIR, NOTES_DIR, PAPERS_DIR, safe_filename


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _relative_to_base(path: Path) -> str:
    return path.resolve().relative_to(BASE_DIR.resolve()).as_posix()


def _unique_path(directory: Path, filename: str) -> Path:
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


def _root_from_name(root_name: str) -> Path:
    if root_name == "papers":
        return PAPERS_DIR
    if root_name == "notes":
        return NOTES_DIR
    raise ValueError("root_name 只能是 'papers' 或 'notes'。")


def list_categories_raw(root_name: str = "notes") -> list[str]:
    """List category folders under ``notes`` or ``papers``."""

    root = _root_from_name(root_name)
    root.mkdir(parents=True, exist_ok=True)
    return sorted(
        [
            item.name
            for item in root.iterdir()
            if item.is_dir() and not item.name.startswith(".")
        ],
        key=str.lower,
    )


def save_note_raw(
    title: str,
    content: str,
    category: str = "论文精读笔记",
) -> dict[str, Any]:
    """Save raw Markdown content into the local note system."""

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    category_name = safe_filename(category, "论文精读笔记")
    folder = NOTES_DIR / category_name
    folder.mkdir(parents=True, exist_ok=True)

    filename = safe_filename(title, "untitled_note")
    if not filename.lower().endswith(".md"):
        filename = f"{filename}.md"
    path = _unique_path(folder, filename)
    path.write_text(content, encoding="utf-8")
    return {
        "ok": True,
        "title": title,
        "category": category_name,
        "path": _relative_to_base(path),
        "absolute_path": str(path.resolve()),
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def list_notes_raw(category: str | None = None) -> list[dict[str, Any]]:
    """List Markdown notes saved under ``notes``."""

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    if category and category != "全部":
        folders = [NOTES_DIR / safe_filename(category)]
    else:
        folders = [NOTES_DIR]

    notes: list[dict[str, Any]] = []
    for folder in folders:
        if not folder.exists():
            continue
        for path in folder.rglob("*.md"):
            if not _is_within(path, NOTES_DIR):
                continue
            stat = path.stat()
            rel_category = path.parent.relative_to(NOTES_DIR).as_posix()
            notes.append(
                {
                    "title": path.stem,
                    "filename": path.name,
                    "category": rel_category if rel_category != "." else "",
                    "path": _relative_to_base(path),
                    "absolute_path": str(path.resolve()),
                    "updated_at": datetime.fromtimestamp(stat.st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "size": stat.st_size,
                }
            )
    return sorted(notes, key=lambda item: item["updated_at"], reverse=True)


def read_note_raw(path: str) -> dict[str, Any]:
    """Read a Markdown note by relative or absolute path."""

    note_path = Path(path)
    if not note_path.is_absolute():
        note_path = BASE_DIR / note_path
    note_path = note_path.resolve()
    if not _is_within(note_path, NOTES_DIR):
        raise ValueError("只能读取 notes/ 目录下的文件。")
    if not note_path.exists():
        raise FileNotFoundError("笔记文件不存在。")
    return {
        "ok": True,
        "path": _relative_to_base(note_path),
        "content": note_path.read_text(encoding="utf-8"),
    }


def list_files_raw(
    root_name: str,
    *,
    category: str | None = None,
    suffixes: tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    """List files under ``papers`` or ``notes`` for the file manager."""

    root = _root_from_name(root_name)
    root.mkdir(parents=True, exist_ok=True)
    folders = [root / safe_filename(category)] if category and category != "全部" else [root]
    files: list[dict[str, Any]] = []
    for folder in folders:
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if not path.is_file() or path.name.startswith("."):
                continue
            if path.name == "metadata.json":
                continue
            if suffixes and path.suffix.lower() not in suffixes:
                continue
            if not _is_within(path, root):
                continue
            stat = path.stat()
            rel_category = path.parent.relative_to(root).as_posix()
            files.append(
                {
                    "filename": path.name,
                    "category": rel_category if rel_category != "." else "",
                    "path": _relative_to_base(path),
                    "absolute_path": str(path.resolve()),
                    "updated_at": datetime.fromtimestamp(stat.st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "size": stat.st_size,
                }
            )
    return sorted(files, key=lambda item: item["updated_at"], reverse=True)


def rename_file_raw(path: str, new_name: str, root_name: str = "notes") -> dict[str, Any]:
    """Rename a file under ``notes`` or ``papers``."""

    root = _root_from_name(root_name)
    source = Path(path)
    if not source.is_absolute():
        source = BASE_DIR / source
    source = source.resolve()
    if not _is_within(source, root):
        raise ValueError("非法文件路径。")
    if not source.exists() or not source.is_file():
        raise FileNotFoundError("文件不存在。")

    new_name = safe_filename(new_name, source.name)
    if not Path(new_name).suffix:
        new_name = f"{new_name}{source.suffix}"
    target = _unique_path(source.parent, new_name)
    source.rename(target)
    return {
        "ok": True,
        "old_path": _relative_to_base(source),
        "path": _relative_to_base(target),
        "absolute_path": str(target.resolve()),
    }


def delete_file_raw(path: str, root_name: str = "notes") -> bool:
    """Delete a single file under ``notes`` or ``papers``."""

    root = _root_from_name(root_name)
    target = Path(path)
    if not target.is_absolute():
        target = BASE_DIR / target
    target = target.resolve()
    if not _is_within(target, root):
        raise ValueError("非法文件路径。")
    if target.exists() and target.is_file():
        target.unlink()
        return True
    return False


def create_category_raw(root_name: str, category: str) -> dict[str, Any]:
    """Create a category folder under ``notes`` or ``papers``."""

    root = _root_from_name(root_name)
    folder = root / safe_filename(category, "未分类")
    folder.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "category": folder.name, "path": _relative_to_base(folder)}


def move_file_raw(
    path: str,
    *,
    root_name: str,
    category: str,
) -> dict[str, Any]:
    """Move a single file into another category folder."""

    root = _root_from_name(root_name)
    source = Path(path)
    if not source.is_absolute():
        source = BASE_DIR / source
    source = source.resolve()
    if not _is_within(source, root):
        raise ValueError("非法文件路径。")
    if not source.exists() or not source.is_file():
        raise FileNotFoundError("文件不存在。")

    folder = root / safe_filename(category, "未分类")
    folder.mkdir(parents=True, exist_ok=True)
    target = _unique_path(folder, source.name)
    shutil.move(str(source), str(target))
    return {"ok": True, "path": _relative_to_base(target)}

