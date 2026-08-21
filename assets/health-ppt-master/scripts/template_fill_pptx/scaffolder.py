"""scaffold: turn a slide library into an editable fill-plan skeleton."""

from __future__ import annotations

from typing import Any


def scaffold_plan(
    library: dict[str, Any],
    selected_slides: list[int] | None = None,
    *,
    include_empty: bool = False,
) -> dict[str, Any]:
    """Build an editable fill plan skeleton from a slide library."""
    selected = set(selected_slides or [])
    source_slides = library.get("slides", [])
    if not selected:
        source_slides = source_slides[: min(6, len(source_slides))]
    else:
        source_slides = [slide for slide in source_slides if int(slide["slide_index"]) in selected]

    slides: list[dict[str, Any]] = []
    for slide in source_slides:
        replacements = []
        for slot in slide.get("slots", []):
            if not include_empty and not str(slot.get("text") or "").strip():
                continue
            replacements.append(
                {
                    "slot_id": slot["slot_id"],
                    "old_text": slot["text"],
                    "text": slot["text"],
                }
            )
        table_edits = []
        for table in slide.get("tables", []):
            table_edits.append(
                {
                    "table_id": table["table_id"],
                    "cells": [
                        {
                            "row": cell["row"],
                            "col": cell["col"],
                            "old_text": cell["text"],
                            "text": cell["text"],
                        }
                        for row in table.get("rows", [])
                        for cell in row.get("cells", [])
                    ],
                }
            )
        chart_edits = []
        for chart in slide.get("charts", []):
            chart_edits.append(
                {
                    "chart_id": chart["chart_id"],
                    "categories": chart.get("categories", []),
                    "series": chart.get("series") or [{"name": "系列1", "values": []}],
                }
            )
        image_edits = []
        for picture in slide.get("pictures", []):
            # Default every source picture to "clear": template-fill clones the
            # whole slide, so an un-handled picture survives as the wrong project's
            # image. The model edits the label, or flips to action "replace" with a
            # new_image path. Leaving the list empty trips the apply image gate.
            image_edits.append(
                {
                    "image_id": picture["image_id"],
                    "action": "clear",
                    "old_media": picture.get("media_target", ""),
                    "label": f"［配图：{picture.get('alt') or '请插入贴合新内容的图'}］",
                }
            )
        slides.append(
            {
                "source_slide": slide["slide_index"],
                "purpose": slide.get("page_type", "content_candidate"),
                "replacements": replacements,
                "table_edits": table_edits,
                "chart_edits": chart_edits,
                "image_edits": image_edits,
            }
        )

    return {
        "schema": "template_fill_pptx_plan.v1",
        "source_pptx": library.get("source_pptx"),
        "slides": slides,
    }
