"""check-plan: compare planned text / table / chart edits against source capacity."""

from __future__ import annotations

import unicodedata
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .ooxml import _parse_slide_refs, _picture_containers, _shape_identity
from .selectors import (
    _chart_selectors,
    _image_selectors,
    _replacement_selectors,
    _replacement_text,
    _table_selectors,
)


def _slot_lookup(library: dict[str, Any]) -> dict[tuple[int, str], dict[str, Any]]:
    lookup: dict[tuple[int, str], dict[str, Any]] = {}
    for slide in library.get("slides", []):
        slide_index = int(slide.get("slide_index", 0))
        for slot in slide.get("slots", []):
            if slot.get("slot_id"):
                lookup[(slide_index, f"slot_id:{slot['slot_id']}")] = slot
            if slot.get("shape_id"):
                lookup[(slide_index, f"shape_id:{slot['shape_id']}")] = slot
            if slot.get("shape_name"):
                lookup[(slide_index, f"shape_name:{slot['shape_name']}")] = slot
    return lookup


def _table_lookup(library: dict[str, Any]) -> dict[tuple[int, str], dict[str, Any]]:
    lookup: dict[tuple[int, str], dict[str, Any]] = {}
    for slide in library.get("slides", []):
        slide_index = int(slide.get("slide_index", 0))
        for table in slide.get("tables", []):
            if table.get("table_id"):
                lookup[(slide_index, f"table_id:{table['table_id']}")] = table
            if table.get("shape_id"):
                lookup[(slide_index, f"shape_id:{table['shape_id']}")] = table
            if table.get("shape_name"):
                lookup[(slide_index, f"shape_name:{table['shape_name']}")] = table
    return lookup


def _chart_lookup(library: dict[str, Any]) -> dict[tuple[int, str], dict[str, Any]]:
    lookup: dict[tuple[int, str], dict[str, Any]] = {}
    for slide in library.get("slides", []):
        slide_index = int(slide.get("slide_index", 0))
        for chart in slide.get("charts", []):
            if chart.get("chart_id"):
                lookup[(slide_index, f"chart_id:{chart['chart_id']}")] = chart
            if chart.get("shape_id"):
                lookup[(slide_index, f"shape_id:{chart['shape_id']}")] = chart
            if chart.get("shape_name"):
                lookup[(slide_index, f"shape_name:{chart['shape_name']}")] = chart
    return lookup


def _picture_lookup(library: dict[str, Any]) -> dict[tuple[int, str], dict[str, Any]]:
    lookup: dict[tuple[int, str], dict[str, Any]] = {}
    for slide in library.get("slides", []):
        slide_index = int(slide.get("slide_index", 0))
        for picture in slide.get("pictures", []):
            if picture.get("image_id"):
                lookup[(slide_index, f"image_id:{picture['image_id']}")] = picture
            if picture.get("shape_id"):
                lookup[(slide_index, f"shape_id:{picture['shape_id']}")] = picture
            if picture.get("shape_name"):
                lookup[(slide_index, f"shape_name:{picture['shape_name']}")] = picture
    return lookup


def _pictures_by_slide(library: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    return {
        int(slide.get("slide_index", 0)): slide.get("pictures", [])
        for slide in library.get("slides", [])
    }


def _visual_width(text: str) -> float:
    """Estimate rendered text width in Latin-character units.

    ``len(text)`` is too crude for mixed CJK / Latin decks: Chinese characters
    generally consume about twice the horizontal space of ASCII letters, while
    punctuation and digits are narrower. The checker only needs a conservative
    fit signal, so use Unicode East Asian Width instead of a font-specific
    renderer.
    """
    width = 0.0
    for char in "".join(text.split()):
        east_asian_width = unicodedata.east_asian_width(char)
        if east_asian_width in {"F", "W"}:
            width += 2.0
        elif east_asian_width == "A":
            width += 1.5
        else:
            width += 1.0
    return width


def _display_width(value: float) -> int | float:
    return int(value) if value.is_integer() else round(value, 1)


def _fallback_font_size_px(role: str, geometry: dict[str, Any], old_paragraphs: int) -> float:
    height = geometry.get("height")
    if isinstance(height, int) and old_paragraphs > 0:
        inferred = height / max(old_paragraphs, 1) / 1.25
        if 8 <= inferred <= 56:
            return inferred
    if role == "title_candidate":
        return 28.0
    if role == "body_candidate":
        return 16.0
    return 14.0


def _geometry_capacity_width(
    *,
    role: str,
    old_paragraphs: int,
    new_paragraphs: int,
    geometry: dict[str, Any],
    text_metrics: dict[str, Any],
) -> float | None:
    width = geometry.get("width")
    height = geometry.get("height")
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        return None

    font_size_px = text_metrics.get("font_size_px")
    if not isinstance(font_size_px, (int, float)) or font_size_px <= 0:
        font_size_px = _fallback_font_size_px(role, geometry, old_paragraphs)

    line_height = max(font_size_px * 1.25, 1.0)
    max_lines = max(int(height / line_height), old_paragraphs, new_paragraphs, 1)
    horizontal_padding = 24 if width >= 180 else 12
    usable_width = max(width - horizontal_padding, width * 0.72, 1)
    latin_units_per_line = usable_width / max(font_size_px * 0.52, 1)
    capacity = latin_units_per_line * max_lines

    if role == "label_candidate":
        return capacity * 0.7
    if role == "title_candidate":
        return capacity * 0.85
    return capacity


def _fit_status(
    *,
    role: str,
    old_width: float,
    new_width: float,
    old_paragraphs: int,
    new_paragraphs: int,
    geometry: dict[str, Any],
    text_metrics: dict[str, Any],
) -> tuple[str, str]:
    old_width = max(old_width, 1.0)
    ratio = new_width / old_width
    width = geometry.get("width")
    height = geometry.get("height")
    capacity_width = _geometry_capacity_width(
        role=role,
        old_paragraphs=old_paragraphs,
        new_paragraphs=new_paragraphs,
        geometry=geometry,
        text_metrics=text_metrics,
    )

    if role == "label_candidate" or (old_width <= 8 and old_paragraphs <= 1):
        if capacity_width is not None and new_width <= capacity_width and not (old_width <= 8):
            return "OK", "short label fits estimated text-box capacity"
        label_limit = old_width
        if isinstance(width, int) and width >= 220:
            label_limit = max(label_limit, old_width * 1.25)
        if new_width > label_limit:
            return "WARN", "short label exceeds original visual width; rewrite shorter"
        return "OK", "short label fits original visual width"

    if role == "title_candidate" and old_paragraphs <= 1:
        if capacity_width is not None and new_width <= capacity_width:
            return "OK", "title fits estimated text-box capacity"
        limit = 1.15 if old_width <= 12 else 1.35
        if ratio > limit:
            return "WARN", "title is too long for the original slot; rewrite first"
        return "OK", "title stays near original capacity"

    paragraph_limit = max(old_paragraphs + 2, old_paragraphs * 2, 2)
    if new_paragraphs > paragraph_limit:
        return "WARN", "body paragraph count changed too much; compress or split pages"

    if isinstance(width, int) and isinstance(height, int) and width * height < 30000 and ratio > 2.0:
        return "WARN", "small text box with much longer text; rewrite shorter"

    if capacity_width is not None and new_width > capacity_width:
        return "WARN", "text exceeds estimated text-box capacity; rewrite or split"

    # Body text reflows, so a moderate amount of extra length is fine; only flag
    # gross overflow. Labels / titles keep their tighter guards above.
    body_limit = 3.0 if role == "body_candidate" else 2.2
    if ratio > body_limit:
        return "WARN", "text is much longer than source slot; rewrite or choose another page"
    return "OK", "within estimated slot capacity"


def _capacity_for_report(
    *,
    role: str,
    old_width: float,
    old_paragraphs: int,
    new_paragraphs: int,
    geometry: dict[str, Any],
    text_metrics: dict[str, Any],
) -> float | None:
    capacity = _geometry_capacity_width(
        role=role,
        old_paragraphs=old_paragraphs,
        new_paragraphs=new_paragraphs,
        geometry=geometry,
        text_metrics=text_metrics,
    )
    if capacity is None:
        return None
    return _display_width(max(capacity, old_width))


def _reuse_collisions(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Source slides reused by >1 output slide.

    ``apply`` clones the *whole* source slide — including its embedded
    images / diagrams / charts, which template-fill v1 does **not** replace.
    Reusing one source slide for several output slides therefore repeats that
    slide's baked-in visuals. Harmless when the layout is generic (a plain
    content page reused for several content slides); a quality killer when the
    source slide carries **topic-specific** graphics — the same diagram then
    appears under several different topics (the 2026-06-18 frankenstein:
    source slide 8 reused for 数据要素底座 / WiseDiag / 西南神外 alike).

    Advisory only — check-plan cannot tell a generic layout from a
    topic-specific one (the library indexes text slots, not pictures), so the
    SOP / model decides whether each reused layout is safe or must be redesigned
    (F3b). Returns one entry per source slide used >= 2x.
    """
    by_source: dict[int, list[dict[str, Any]]] = {}
    for idx, slide in enumerate(plan.get("slides", []), start=1):
        try:
            src = int(slide.get("source_slide", 0))
        except (TypeError, ValueError):
            continue
        label = str(slide.get("purpose") or slide.get("note") or "").strip()
        by_source.setdefault(src, []).append({"plan_slide": idx, "label": label[:60]})
    collisions: list[dict[str, Any]] = []
    for src, pages in sorted(by_source.items()):
        if len(pages) >= 2:
            collisions.append(
                {
                    "source_slide": src,
                    "reuse_count": len(pages),
                    "plan_slides": [p["plan_slide"] for p in pages],
                    "labels": [p["label"] for p in pages],
                }
            )
    return collisions


def _picture_identities(slide_root: ET.Element, source_slide: int) -> list[dict[str, str]]:
    """``<p:pic>`` identities (image_id / shape_id / shape_name) on a slide.

    Built the same way ``analyzer`` and ``image_fill`` build them, so a plan's
    ``image_edits`` selectors match here, in check-plan, and at apply identically.
    """
    identities: list[dict[str, str]] = []
    for order, pic in enumerate(_picture_containers(slide_root), start=1):
        shape_id, shape_name = _shape_identity(pic, order)
        identities.append(
            {
                "image_id": f"s{source_slide:02d}_pic{shape_id}",
                "shape_id": shape_id,
                "shape_name": shape_name,
            }
        )
    return identities


def _picture_handled(picture: dict[str, str], image_edits: list[dict[str, Any]]) -> bool:
    """True if some image_edit selector targets this picture (clear or replace)."""
    keys = set()
    if picture.get("image_id"):
        keys.add(f"image_id:{picture['image_id']}")
    if picture.get("shape_id"):
        keys.add(f"shape_id:{picture['shape_id']}")
    if picture.get("shape_name"):
        keys.add(f"shape_name:{picture['shape_name']}")
    for edit in image_edits:
        if any(selector in keys for selector in _image_selectors(edit)):
            return True
    return False


def _unhandled_pictures(
    pictures: list[dict[str, Any]], image_edits: list[dict[str, Any]]
) -> list[dict[str, str]]:
    """Pictures with no matching image_edit — the wrong-project / patient-photo risk."""
    edits = image_edits if isinstance(image_edits, list) else []
    return [
        {
            "image_id": str(pic.get("image_id") or ""),
            "shape_id": str(pic.get("shape_id") or ""),
            "shape_name": str(pic.get("shape_name") or ""),
        }
        for pic in pictures
        if not _picture_handled(pic, edits)
    ]


def image_block_report(pptx_path: str | Path, plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Output slides that keep an embedded ``<p:pic>`` no image_edit clears/replaces.

    Empty list ⇒ safe to apply. ``apply`` clones the whole source slide, so an
    un-handled picture survives verbatim — the wrong project's photo / a patient
    image. Opens the source PPTX because the picture set lives in the slide XML.
    Fail-soft: an unreadable PPTX never blocks (returns []).
    """
    plan_slides = plan.get("slides")
    if not isinstance(plan_slides, list) or not plan_slides:
        return []
    blocking: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(pptx_path) as zf:
            refs = {ref.index: ref for ref in _parse_slide_refs(zf)}
            for index, slide in enumerate(plan_slides, start=1):
                try:
                    source_slide = int(slide.get("source_slide", 0))
                except (TypeError, ValueError):
                    continue
                ref = refs.get(source_slide)
                if ref is None:
                    continue
                try:
                    slide_root = ET.fromstring(zf.read(ref.part_name))
                except (KeyError, ET.ParseError):
                    continue
                identities = _picture_identities(slide_root, source_slide)
                if not identities:
                    continue
                image_edits = slide.get("image_edits", [])
                unhandled = _unhandled_pictures(identities, image_edits)
                if unhandled:
                    label = str(slide.get("purpose") or slide.get("note") or "").strip()[:60]
                    blocking.append(
                        {
                            "plan_slide": index,
                            "source_slide": source_slide,
                            "label": label,
                            "unhandled": [pic["image_id"] for pic in unhandled],
                        }
                    )
    except (zipfile.BadZipFile, FileNotFoundError, OSError):
        return []
    return blocking


def format_image_refusal(blocking: list[dict[str, Any]]) -> str:
    """Human-facing message for the apply image gate — fix first, override last."""
    total = sum(len(b["unhandled"]) for b in blocking)
    lines = [
        "REFUSED: apply blocked by the template-fill image gate.",
        "",
        f"{total} embedded picture(s) across {len(blocking)} output slide(s) are kept un-handled.",
        "template-fill clones the whole source slide, so these pictures ride into the new deck",
        "verbatim — the wrong project's photo/diagram, or patient imagery. Address every picture",
        "with an image_edit before applying.",
        "",
    ]
    for b in blocking:
        suffix = f"  [{b['label']}]" if b["label"] else ""
        lines.append(
            f"  output P{b['plan_slide']:02d} (source {b['source_slide']}): {b['unhandled']}{suffix}"
        )
    lines += [
        "",
        "Resolve before applying (per picture, in the plan's per-slide image_edits):",
        '  • clear   → {"image_id": "...", "action": "clear", "label": "［配图：…］"}',
        "    (drops the old picture, leaves an editable captioned placeholder of the same size)",
        '  • replace → {"image_id": "...", "action": "replace", "new_image": "/path/to.png"}',
        "  De-identification HARD gate: patient faces / real case images must never survive.",
        "  Pass --allow-source-images ONLY if every kept picture is generic (logo / decorative).",
        "",
        "No file was written.",
    ]
    return "\n".join(lines)


def check_plan(library: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """Compare fill replacements against source slot capacity."""
    lookup = _slot_lookup(library)
    table_lookup = _table_lookup(library)
    chart_lookup = _chart_lookup(library)
    picture_lookup = _picture_lookup(library)
    pictures_by_slide = _pictures_by_slide(library)
    results: list[dict[str, Any]] = []
    summary = {"ok": 0, "warn": 0, "error": 0}
    unhandled_all: list[dict[str, Any]] = []

    for slide_index, slide in enumerate(plan.get("slides", []), start=1):
        source_slide = int(slide.get("source_slide", 0))
        replacements = slide.get("replacements", [])
        if not isinstance(replacements, list):
            results.append(
                {
                    "status": "ERROR",
                    "plan_slide": slide_index,
                    "source_slide": source_slide,
                    "message": "replacements must be a list",
                }
            )
            summary["error"] += 1
            continue

        for replacement in replacements:
            selectors = _replacement_selectors(replacement)
            slot = next((lookup.get((source_slide, selector)) for selector in selectors), None)
            text = _replacement_text(replacement)
            if slot is None:
                results.append(
                    {
                        "status": "ERROR",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "selector": selectors[0] if selectors else "",
                        "message": "replacement target not found in slide library",
                    }
                )
                summary["error"] += 1
                continue

            old_text = str(slot.get("text") or "")
            old_width = _visual_width(old_text)
            new_width = _visual_width(text)
            old_paragraphs = int(slot.get("paragraph_count") or 1)
            new_paragraphs = max(len([line for line in text.splitlines() if line.strip()]), 1)
            status, message = _fit_status(
                role=str(slot.get("role") or ""),
                old_width=old_width,
                new_width=new_width,
                old_paragraphs=old_paragraphs,
                new_paragraphs=new_paragraphs,
                geometry=slot.get("geometry") or {},
                text_metrics=slot.get("text_metrics") or {},
            )
            capacity_width = _capacity_for_report(
                role=str(slot.get("role") or ""),
                old_width=old_width,
                old_paragraphs=old_paragraphs,
                new_paragraphs=new_paragraphs,
                geometry=slot.get("geometry") or {},
                text_metrics=slot.get("text_metrics") or {},
            )
            summary["warn" if status == "WARN" else "ok"] += 1
            results.append(
                {
                    "status": status,
                    "plan_slide": slide_index,
                    "source_slide": source_slide,
                    "slot_id": slot.get("slot_id"),
                    "role": slot.get("role"),
                    "old_len": _display_width(old_width),
                    "new_len": _display_width(new_width),
                    "old_visual_width": _display_width(old_width),
                    "new_visual_width": _display_width(new_width),
                    "capacity_visual_width": capacity_width,
                    "ratio": round(new_width / max(old_width, 1.0), 2),
                    "old_paragraphs": old_paragraphs,
                    "new_paragraphs": new_paragraphs,
                    "message": message,
                    "old_text": old_text,
                    "new_text": text,
                }
            )
        table_edits = slide.get("table_edits", [])
        if not isinstance(table_edits, list):
            results.append(
                {
                    "status": "ERROR",
                    "plan_slide": slide_index,
                    "source_slide": source_slide,
                    "message": "table_edits must be a list",
                }
            )
            summary["error"] += 1
            continue
        for table_edit in table_edits:
            selectors = _table_selectors(table_edit)
            table = next((table_lookup.get((source_slide, selector)) for selector in selectors), None)
            if table is None:
                results.append(
                    {
                        "status": "ERROR",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "selector": selectors[0] if selectors else "",
                        "message": "table target not found in slide library",
                    }
                )
                summary["error"] += 1
                continue
            cells = table_edit.get("cells", [])
            if not isinstance(cells, list):
                results.append(
                    {
                        "status": "ERROR",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "selector": selectors[0] if selectors else "",
                        "message": "table edit cells must be a list",
                    }
                )
                summary["error"] += 1
                continue
            row_count = int(table.get("row_count") or 0)
            column_count = int(table.get("column_count") or 0)
            for cell in cells:
                row = int(cell.get("row", -1))
                col = int(cell.get("col", -1))
                if row < 0 or col < 0 or row >= row_count or col >= column_count:
                    results.append(
                        {
                            "status": "ERROR",
                            "plan_slide": slide_index,
                            "source_slide": source_slide,
                            "selector": selectors[0] if selectors else "",
                            "message": f"table cell out of bounds: row={row} col={col}",
                        }
                    )
                    summary["error"] += 1
                    continue
                summary["ok"] += 1
                results.append(
                    {
                        "status": "OK",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "table_id": table.get("table_id"),
                        "row": row,
                        "col": col,
                        "message": "table cell target exists",
                    }
                )
        chart_edits = slide.get("chart_edits", [])
        if not isinstance(chart_edits, list):
            results.append(
                {
                    "status": "ERROR",
                    "plan_slide": slide_index,
                    "source_slide": source_slide,
                    "message": "chart_edits must be a list",
                }
            )
            summary["error"] += 1
            continue
        for chart_edit in chart_edits:
            selectors = _chart_selectors(chart_edit)
            chart = next((chart_lookup.get((source_slide, selector)) for selector in selectors), None)
            if chart is None:
                results.append(
                    {
                        "status": "ERROR",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "selector": selectors[0] if selectors else "",
                        "message": "chart target not found in slide library",
                    }
                )
                summary["error"] += 1
                continue
            categories = chart_edit.get("categories", [])
            series = chart_edit.get("series", [])
            if not isinstance(categories, list) or not isinstance(series, list) or not series:
                results.append(
                    {
                        "status": "ERROR",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "selector": selectors[0] if selectors else "",
                        "message": "chart edit requires categories list and non-empty series list",
                    }
                )
                summary["error"] += 1
                continue
            bad_series = [
                item
                for item in series
                if not isinstance(item, dict)
                or not isinstance(item.get("values", []), list)
                or len(item.get("values", [])) != len(categories)
            ]
            if bad_series:
                results.append(
                    {
                        "status": "ERROR",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "selector": selectors[0] if selectors else "",
                        "message": "each chart series needs values matching categories length",
                    }
                )
                summary["error"] += 1
                continue
            summary["ok"] += 1
            results.append(
                {
                    "status": "OK",
                    "plan_slide": slide_index,
                    "source_slide": source_slide,
                    "chart_id": chart.get("chart_id"),
                    "category_count": len(categories),
                    "series_count": len(series),
                    "message": "chart edit target and data shape are valid",
                }
            )
        image_edits = slide.get("image_edits", [])
        if not isinstance(image_edits, list):
            results.append(
                {
                    "status": "ERROR",
                    "plan_slide": slide_index,
                    "source_slide": source_slide,
                    "message": "image_edits must be a list",
                }
            )
            summary["error"] += 1
            image_edits = []
        for image_edit in image_edits:
            selectors = _image_selectors(image_edit)
            picture = next((picture_lookup.get((source_slide, selector)) for selector in selectors), None)
            if picture is None:
                results.append(
                    {
                        "status": "ERROR",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "selector": selectors[0] if selectors else "",
                        "message": "image target not found in slide library",
                    }
                )
                summary["error"] += 1
                continue
            action = str(image_edit.get("action") or "clear").lower()
            if action not in {"clear", "replace"}:
                results.append(
                    {
                        "status": "ERROR",
                        "plan_slide": slide_index,
                        "source_slide": source_slide,
                        "selector": selectors[0] if selectors else "",
                        "message": f"image edit action must be 'clear' or 'replace', got '{action}'",
                    }
                )
                summary["error"] += 1
                continue
            if action == "replace":
                new_image = str(image_edit.get("new_image") or "")
                if not new_image:
                    results.append(
                        {
                            "status": "ERROR",
                            "plan_slide": slide_index,
                            "source_slide": source_slide,
                            "selector": selectors[0] if selectors else "",
                            "message": "image edit action 'replace' requires new_image",
                        }
                    )
                    summary["error"] += 1
                    continue
                if not Path(new_image).expanduser().is_file():
                    summary["warn"] += 1
                    results.append(
                        {
                            "status": "WARN",
                            "plan_slide": slide_index,
                            "source_slide": source_slide,
                            "selector": selectors[0] if selectors else "",
                            "message": f"new_image not found yet (apply will fail if still missing): {new_image}",
                        }
                    )
                    continue
            summary["ok"] += 1
            results.append(
                {
                    "status": "OK",
                    "plan_slide": slide_index,
                    "source_slide": source_slide,
                    "image_id": picture.get("image_id"),
                    "action": action,
                    "message": f"image edit target exists ({action})",
                }
            )
        unhandled = _unhandled_pictures(pictures_by_slide.get(source_slide, []), image_edits)
        if unhandled:
            unhandled_all.append(
                {
                    "plan_slide": slide_index,
                    "source_slide": source_slide,
                    "label": str(slide.get("purpose") or slide.get("note") or "").strip()[:60],
                    "unhandled": [pic.get("image_id", "") for pic in unhandled],
                }
            )
    reuse = _reuse_collisions(plan)
    summary["reused_sources"] = len(reuse)
    summary["unhandled_pictures"] = sum(len(u["unhandled"]) for u in unhandled_all)
    return {
        "schema": "template_fill_pptx_check.v1",
        "summary": summary,
        "results": results,
        "reuse": reuse,
        "unhandled_pictures": unhandled_all,
    }


def print_check_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print(f"check-plan: ok={summary['ok']} warn={summary['warn']} error={summary['error']}")
    for item in report["results"]:
        if item["status"] == "OK":
            continue
        if "ratio" in item:
            line = (
                "{status} P{plan_slide:02d} source={source_slide} {slot_id} "
                "{role} old={old_len} new={new_len} ratio={ratio}: {message}".format(**item)
            )
        else:
            target = item.get("slot_id") or item.get("selector") or ""
            line = (
                f"{item['status']} P{item['plan_slide']:02d} "
                f"source={item['source_slide']} {target}: {item['message']}".strip()
            )
        print(line)
    reuse = report.get("reuse") or []
    if reuse:
        print(
            f"reuse: {len(reuse)} source slide(s) reused by multiple output slides — "
            f"apply clones each whole slide incl. its (un-replaced) images/diagrams; "
            f"verify the layout is generic, else the same visual repeats across topics "
            f"(redesign those pages via F3b reverse-redesign)."
        )
        for c in reuse:
            labels = " | ".join(label for label in c["labels"] if label)
            suffix = f" [{labels}]" if labels else ""
            print(
                f"REUSE source={c['source_slide']} x{c['reuse_count']} -> "
                f"plan slides {c['plan_slides']}{suffix}"
            )
    unhandled = report.get("unhandled_pictures") or []
    if unhandled:
        total = sum(len(u["unhandled"]) for u in unhandled)
        print(
            f"images: {total} embedded picture(s) across {len(unhandled)} output slide(s) have no "
            f"image_edit — apply will REFUSE (these clone the source's pictures verbatim: wrong-project "
            f"photos / patient imagery). Add an image_edit (clear/replace) per picture, or --allow-source-images."
        )
        for u in unhandled:
            suffix = f" [{u['label']}]" if u["label"] else ""
            print(
                f"IMAGES P{u['plan_slide']:02d} source={u['source_slide']} unhandled {u['unhandled']}{suffix}"
            )
