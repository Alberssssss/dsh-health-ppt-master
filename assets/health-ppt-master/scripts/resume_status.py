#!/usr/bin/env python3
"""resume_status.py — report which design_spec §IX pages are already generated
(present + well-formed) in svg_output/, so Executor Step 6 can RESUME a dropped or
partial Phase-B run instead of regenerating every page (ADR-0052).

Why: the self-hosted GLM endpoint has no prompt cache, a ~137K input ceiling, and
long sessions drop. Phase B (sequential per-page SVG generation) is the longest
single session in the pipeline; a 20-page deck that dies at page 14 must NOT restart
from page 1. This reads the §IX roster + svg_output/ and prints DONE / INVALID /
MISSING by slide index so the model generates ONLY the gap, in roster order.

A page is DONE when its `<NN>_*.svg` exists and parses as well-formed XML. A page
written half-way when the session dropped parses as broken → INVALID → regenerate.

Usage:
    python3 scripts/resume_status.py <project_path>

Exit code: always 0 — this is a status reporter, never a gate.
"""

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

# §IX "Content Outline" slide headings: "#### Slide 01 - Cover" / "### Slide 2: 概述".
# Tolerant of heading depth (### or ####), separators (- – — : .), and no title.
_SLIDE_RE = re.compile(
    r'^\s*#{2,4}\s*Slide\s+(\d+)\s*[-–—:.、)]?\s*(.*)$',
    re.IGNORECASE | re.MULTILINE,
)


def parse_roster(design_spec: Path):
    """Ordered [(idx:int, 'NN', title)] from design_spec.md §IX. Empty if unparseable."""
    try:
        text = design_spec.read_text(encoding='utf-8')
    except OSError:
        return []
    out, seen = [], set()
    for m in _SLIDE_RE.finditer(text):
        idx = int(m.group(1))
        if idx in seen:
            continue
        seen.add(idx)
        out.append((idx, str(idx).zfill(2), m.group(2).strip()))
    return out


def _svg_index(path: Path):
    """Leading numeric index of an `<NN>_name.svg` file, or None if not indexed."""
    m = re.match(r'^(\d+)', path.stem)
    return int(m.group(1)) if m else None


def _is_well_formed(path: Path) -> bool:
    try:
        ET.parse(str(path))
        return True
    except (ET.ParseError, OSError):
        return False


def scan(project_path: str):
    """Return (roster, present, unindexed, has_spec).

    present:   {idx: (filename, is_valid)}
    unindexed: [(filename, is_valid)] for svgs without an NN prefix
    """
    proj = Path(project_path)
    design = proj / 'design_spec.md'
    svg_dir = proj / 'svg_output'
    roster = parse_roster(design)

    present: dict[int, tuple[str, bool]] = {}
    unindexed: list[tuple[str, bool]] = []
    if svg_dir.is_dir():
        for p in sorted(svg_dir.glob('*.svg')):
            idx = _svg_index(p)
            valid = _is_well_formed(p)
            if idx is None:
                unindexed.append((p.name, valid))
            else:
                # first valid wins; keep an invalid record only if no valid seen
                if idx not in present or (valid and not present[idx][1]):
                    present[idx] = (p.name, valid)
    return roster, present, unindexed, design.is_file()


def build_report(project_path: str) -> str:
    roster, present, unindexed, has_spec = scan(project_path)
    lines: list[str] = []
    lines.append(f"[resume_status] project: {project_path}")

    if not roster:
        # No parseable §IX roster — degrade gracefully, list what's on disk.
        if not has_spec:
            lines.append("  design_spec.md not found — cannot read the §IX roster.")
        else:
            lines.append("  Could not parse a `#### Slide NN - …` roster from §IX "
                         "(legacy / free-structure deck).")
        valid = [n for n, v in unindexed if v] + \
                [f"{fn}" for _i, (fn, v) in sorted(present.items()) if v]
        invalid = [n for n, v in unindexed if not v] + \
                  [f"{fn}" for _i, (fn, v) in sorted(present.items()) if not v]
        lines.append(f"  svg_output present & valid ({len(valid)}): "
                     f"{', '.join(valid) if valid else '(none)'}")
        if invalid:
            lines.append(f"  present but MALFORMED ({len(invalid)}): {', '.join(invalid)} "
                         "→ regenerate these")
        lines.append("  → Cannot map to a roster automatically; resume against your own "
                     "§IX page plan: generate the pages not listed above, in order.")
        return "\n".join(lines)

    done, invalid, missing = [], [], []
    for idx, nn, title in roster:
        rec = present.get(idx)
        label = f"{nn} {title}".rstrip()
        if rec is None:
            missing.append(label)
        elif rec[1]:
            done.append(label)
        else:
            invalid.append(f"{label}  ({rec[0]})")

    total = len(roster)
    lines.append(f"  §IX roster: {total} slides | DONE {len(done)} | "
                 f"INVALID {len(invalid)} | MISSING {len(missing)}")

    # orphans: svgs present on disk not in the roster (informational)
    roster_idx = {idx for idx, _n, _t in roster}
    orphans = [f"{fn}" for i, (fn, _v) in sorted(present.items()) if i not in roster_idx]
    orphans += [fn for fn, _v in unindexed]

    if not missing and not invalid:
        lines.append(f"  ✅ COMPLETE — all {total} pages present & well-formed. "
                     "Skip generation; run svg_quality_checker.py then Step 7.")
        if orphans:
            lines.append(f"  note: {len(orphans)} svg not in §IX roster: {', '.join(orphans)}")
        return "\n".join(lines)

    resume = invalid + missing  # regenerate malformed, then fill gaps
    # keep resume list in roster order
    order = {f"{nn} {title}".rstrip(): i for i, (idx, nn, title) in enumerate(roster)}

    def _key(entry: str) -> int:
        base = entry.split("  (")[0]
        return order.get(base, 10**6)

    resume_sorted = sorted(resume, key=_key)
    lines.append("  ▶ RESUME — generate ONLY these, in this order "
                 "(sequential, one at a time — this is not batching):")
    for e in resume_sorted:
        lines.append(f"      - {e}")
    if done:
        lines.append(f"  Already DONE (do NOT regenerate): "
                     f"{', '.join(d.split()[0] for d in done)}")
        lines.append("  Tip: read_file 1–2 DONE pages first for visual consistency.")
    if orphans:
        lines.append(f"  note: {len(orphans)} svg not in §IX roster: {', '.join(orphans)}")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python3 resume_status.py <project_path>")
        return 0
    print(build_report(sys.argv[1]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
