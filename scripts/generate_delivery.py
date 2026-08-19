#!/usr/bin/env python3
"""Wrap the generated Markdown report and HTML path in a fixed final response."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKERS = ("{{report_markdown}}", "{{html_path}}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "references" / "04-output" / "04-final-delivery-template.md",
    )
    args = parser.parse_args()
    if not args.markdown.is_file():
        raise FileNotFoundError(f"Markdown report not found: {args.markdown}")
    if not args.html.is_file():
        raise FileNotFoundError(f"HTML report not found: {args.html}")
    template = args.template.read_text(encoding="utf-8")
    if any(marker not in template for marker in MARKERS):
        raise ValueError("Final delivery template is missing a required marker")
    rendered = template.replace("{{report_markdown}}", args.markdown.read_text(encoding="utf-8").rstrip())
    rendered = rendered.replace("{{html_path}}", str(args.html.resolve()))
    if "{{" in rendered or "}}" in rendered:
        raise ValueError("Final delivery template contains unreplaced markers")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered.rstrip() + "\n")
    print(f"saved: {args.output}")


if __name__ == "__main__":
    main()
