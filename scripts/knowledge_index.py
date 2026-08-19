#!/usr/bin/env python3
"""Build and query a compact heading index without emitting document bodies."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


TEXT_EXTENSIONS = {".md"}
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")


def scan(path: Path, root: Path) -> dict[str, object]:
    headings: list[dict[str, object]] = []
    first_text = ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if stripped and not first_text:
                    first_text = stripped[:200]
                match = HEADING.match(line)
                if match:
                    headings.append({"line": number, "level": len(match.group(1)), "title": match.group(2)[:300]})
    except OSError as exc:
        return {"path": str(path.relative_to(root)), "error": str(exc), "headings": []}
    return {
        "path": str(path.relative_to(root)),
        "size_bytes": path.stat().st_size,
        "title_hint": first_text,
        "headings": headings,
    }


def score(entry: dict[str, object], terms: list[str]) -> int:
    text = " ".join(
        [str(entry.get("path", "")), str(entry.get("title_hint", ""))]
        + [str(item.get("title", "")) for item in entry.get("headings", []) if isinstance(item, dict)]
    ).casefold()
    return sum(3 if term in str(entry.get("path", "")).casefold() else 1 for term in terms if term in text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parent.parent / "knowledge"
    default_output = Path(__file__).resolve().parent.parent / "data" / "knowledge-index.json"
    parser.add_argument("--root", type=Path, default=default_root, help="Flat Markdown knowledge directory")
    parser.add_argument("--output", type=Path, default=default_output, help="Index JSON output path")
    parser.add_argument("--query", help="Optional space-separated terms used to print only top candidates")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"Knowledge root is not a directory: {root}")
    entries = [scan(path, root) for path in sorted(root.glob("*.md")) if path.is_file()]
    index = {
        "schema_version": "1.0",
        "root": str(root),
        "format": "flat-markdown",
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "documents": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result: dict[str, object] = {"saved": str(args.output), "document_count": len(entries)}
    if args.query:
        terms = [term.casefold() for term in args.query.split() if term.strip()]
        ranked = sorted(((score(entry, terms), entry) for entry in entries), key=lambda item: item[0], reverse=True)
        result["matches"] = [entry for rank, entry in ranked if rank > 0][: max(1, args.limit)]
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
