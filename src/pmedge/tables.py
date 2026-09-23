"""Readers for the two table formats the source projects emit.

Markdown pipe tables (the daily reports) and pandas `to_string` blocks (the research
scripts). Both return lists of dicts of strings; conversion to numbers is the caller's job,
so a parsing error never silently becomes a number.
"""
from __future__ import annotations

import re
from pathlib import Path


def md_tables_after(text: str, heading: str) -> list[list[dict[str, str]]]:
    """All pipe tables between `heading` and the next heading of the same or higher level."""
    lines = text.splitlines()
    level = len(heading) - len(heading.lstrip("#"))
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == heading.strip())
    except StopIteration:
        raise KeyError(f"heading not found: {heading!r}")
    block = []
    for line in lines[start + 1:]:
        m = re.match(r"^(#+) ", line)
        if m and len(m.group(1)) <= level:
            break
        block.append(line)
    tables, current = [], []
    for line in block + [""]:
        if line.startswith("|"):
            current.append(line)
        elif current:
            tables.append(_parse_pipe(current))
            current = []
    if not tables:
        raise KeyError(f"no table under {heading!r}")
    return tables


def md_table(text: str, heading: str, index: int = 0) -> list[dict[str, str]]:
    return md_tables_after(text, heading)[index]


def _parse_pipe(rows: list[str]) -> list[dict[str, str]]:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    header, body = cells[0], [c for c in cells[2:]]
    return [dict(zip(header, r)) for r in body]


def text_section(text: str, number: int) -> list[str]:
    """Lines of the `== N. title` section of a research script output."""
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith(f"== {number}."))
    out = []
    for line in lines[start + 1:]:
        if line.startswith("== "):
            break
        out.append(line)
    return out


def fixed_width(lines: list[str]) -> list[dict[str, str]]:
    """Parse a pandas to_string block: right-aligned columns, header on the first line.

    Column boundaries are the end positions of the header names. A row must have a
    non-blank character at every column end, as right-aligned pandas output does; free text
    lines (notes such as 'stat = ...') fail that test and are ignored.
    """
    lines = [l for l in lines if l.strip()]
    header = lines[0]
    names = [(m.group(0), m.end()) for m in re.finditer(r"\S+", header)]
    rows = []
    for line in lines[1:]:
        if any(len(line) < end or line[end - 1] == " " for _, end in names):
            continue
        cells, prev = {}, 0
        for i, (name, end) in enumerate(names):
            stop = len(line) if i == len(names) - 1 else end
            cells[name] = line[prev:stop].strip()
            prev = stop
        rows.append(cells)
    return rows


def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def num(s: str) -> float:
    """Number from a report cell: accepts thousands separators, rejects anything else."""
    s = s.replace(",", "").strip()
    if not re.fullmatch(r"[-+]?\d+(\.\d+)?", s):
        raise ValueError(f"not a number: {s!r}")
    return float(s)
