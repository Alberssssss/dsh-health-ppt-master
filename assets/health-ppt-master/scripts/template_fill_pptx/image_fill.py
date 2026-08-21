"""apply: clear or replace embedded pictures on cloned slides.

template-fill clones a whole source slide, so any ``<p:pic>`` is baked into the
output verbatim — which is wrong when the source deck belongs to a different
project (the wrong photo/diagram rides along) or carries patient imagery. This
stage acts on the plan's per-slide ``image_edits``:

* ``clear``   — drop the picture and drop an editable placeholder ``<p:sp>`` of
  the same geometry in its place (light box + caption). Pure OOXML, no new media.
* ``replace`` — point the picture at a fresh copy of a supplied image file,
  keeping the frame's position / size / crop.

Each ``replace`` mints its OWN media part + relationship and repoints only that
picture's blip, so reusing one source slide for several output slides never lets
one slide's replacement bleed onto its siblings (``clone.py`` keeps media shared).
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .ooxml import (
    IMAGE_REL_TYPE,
    NS,
    REL_NS,
    _blip_embed_rid,
    _picture_containers,
    _qn,
    _shape_identity,
)
from .package import _add_content_type_default, _find_relationship, _max_numeric_rid, _relative_target
from .selectors import _image_selectors

_IMAGE_CONTENT_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "svg": "image/svg+xml",
    "emf": "image/x-emf",
    "wmf": "image/x-wmf",
    "webp": "image/webp",
}

_PLACEHOLDER_FILL = "EEF2F7"
_PLACEHOLDER_LINE = "B8C4D0"
_PLACEHOLDER_TEXT = "5A6B7B"


def _image_content_type(extension: str) -> str:
    extension = extension.lstrip(".").lower()
    return _IMAGE_CONTENT_TYPES.get(extension, f"image/{extension}")


def _picture_key_maps(slide_root: ET.Element, source_slide: int) -> dict[str, dict[str, Any]]:
    maps: dict[str, dict[str, Any]] = {}
    for order, pic in enumerate(_picture_containers(slide_root), start=1):
        shape_id, shape_name = _shape_identity(pic, order)
        info = {
            "element": pic,
            "shape_id": shape_id,
            "shape_name": shape_name,
            "embed_rid": _blip_embed_rid(pic),
        }
        maps[f"image_id:s{source_slide:02d}_pic{shape_id}"] = info
        maps[f"shape_id:{shape_id}"] = info
        if shape_name:
            maps[f"shape_name:{shape_name}"] = info
    return maps


def _placeholder_shape(pic: ET.Element, label: str, shape_id: str) -> ET.Element:
    """An editable rectangle (same geometry as ``pic``) with a centered caption."""
    p, a = NS["p"], NS["a"]
    sp = ET.Element(_qn(p, "sp"))
    nv = ET.SubElement(sp, _qn(p, "nvSpPr"))
    ET.SubElement(nv, _qn(p, "cNvPr"), {"id": str(shape_id), "name": f"image_placeholder_{shape_id}"})
    ET.SubElement(nv, _qn(p, "cNvSpPr"))
    ET.SubElement(nv, _qn(p, "nvPr"))

    sp_pr = ET.SubElement(sp, _qn(p, "spPr"))
    pic_sp_pr = pic.find(_qn(p, "spPr"))
    xfrm = pic_sp_pr.find(_qn(a, "xfrm")) if pic_sp_pr is not None else None
    if xfrm is not None:
        sp_pr.append(copy.deepcopy(xfrm))
    prst = ET.SubElement(sp_pr, _qn(a, "prstGeom"), {"prst": "rect"})
    ET.SubElement(prst, _qn(a, "avLst"))
    fill = ET.SubElement(sp_pr, _qn(a, "solidFill"))
    ET.SubElement(fill, _qn(a, "srgbClr"), {"val": _PLACEHOLDER_FILL})
    ln = ET.SubElement(sp_pr, _qn(a, "ln"))
    ln_fill = ET.SubElement(ln, _qn(a, "solidFill"))
    ET.SubElement(ln_fill, _qn(a, "srgbClr"), {"val": _PLACEHOLDER_LINE})

    tx_body = ET.SubElement(sp, _qn(p, "txBody"))
    ET.SubElement(tx_body, _qn(a, "bodyPr"), {"anchor": "ctr", "wrap": "square"})
    ET.SubElement(tx_body, _qn(a, "lstStyle"))
    para = ET.SubElement(tx_body, _qn(a, "p"))
    ET.SubElement(para, _qn(a, "pPr"), {"algn": "ctr"})
    run = ET.SubElement(para, _qn(a, "r"))
    r_pr = ET.SubElement(run, _qn(a, "rPr"), {"lang": "zh-CN", "sz": "1200"})
    run_fill = ET.SubElement(r_pr, _qn(a, "solidFill"))
    ET.SubElement(run_fill, _qn(a, "srgbClr"), {"val": _PLACEHOLDER_TEXT})
    text = ET.SubElement(run, _qn(a, "t"))
    text.text = label
    return sp


def _set_blip_embed(pic: ET.Element, rel_id: str) -> bool:
    embed = _qn(NS["r"], "embed")
    link = _qn(NS["r"], "link")
    for blip in pic.findall(".//a:blip", NS):
        if blip.attrib.get(embed) or blip.attrib.get(link):
            blip.set(embed, rel_id)
            blip.attrib.pop(link, None)
            return True
    return False


def _apply_image_edits_to_slide_package(
    slide_root: ET.Element,
    rels_root: ET.Element,
    entries: dict[str, bytes],
    content_root: ET.Element,
    *,
    source_slide: int,
    new_slide_part: str,
    image_edits: list[dict[str, Any]],
    next_media_number: int,
) -> int:
    """Apply one slide's image_edits in place. Returns the new media-part high-water mark."""
    if not image_edits:
        return next_media_number
    maps = _picture_key_maps(slide_root, source_slide)
    parent_map = {child: parent for parent in slide_root.iter() for child in parent}
    next_rid = _max_numeric_rid(rels_root) + 1
    errors: list[str] = []
    touched_embed_rids: set[str] = set()

    for edit in image_edits:
        selectors = _image_selectors(edit)
        info = next((maps[key] for key in selectors if key in maps), None)
        if info is None:
            if edit.get("optional"):
                continue
            errors.append(", ".join(selectors) or "<missing selector>")
            continue
        pic = info["element"]
        if info.get("embed_rid"):
            touched_embed_rids.add(info["embed_rid"])
        action = str(edit.get("action") or "clear").lower()

        if action == "clear":
            label = str(edit.get("label") or "［配图：请插入贴合新内容的图］")
            parent = parent_map.get(pic)
            if parent is None:
                errors.append(f"{selectors[0]} (cannot locate picture parent)")
                continue
            index = list(parent).index(pic)
            parent.remove(pic)
            parent.insert(index, _placeholder_shape(pic, label, info["shape_id"]))
        elif action == "replace":
            new_image = edit.get("new_image")
            if not new_image:
                errors.append(f"{selectors[0]} (replace needs new_image)")
                continue
            image_path = Path(str(new_image)).expanduser()
            if not image_path.is_file():
                errors.append(f"{selectors[0]} (new_image not found: {new_image})")
                continue
            extension = image_path.suffix.lstrip(".").lower() or "png"
            next_media_number += 1
            new_media_part = f"ppt/media/image{next_media_number}.{extension}"
            entries[new_media_part] = image_path.read_bytes()
            _add_content_type_default(content_root, extension, _image_content_type(extension))
            rel_id = f"rId{next_rid}"
            next_rid += 1
            ET.SubElement(
                rels_root,
                _qn(REL_NS, "Relationship"),
                {
                    "Id": rel_id,
                    "Type": IMAGE_REL_TYPE,
                    "Target": _relative_target(new_slide_part, new_media_part),
                },
            )
            if not _set_blip_embed(pic, rel_id):
                errors.append(f"{selectors[0]} (picture has no blip to repoint)")
        else:
            errors.append(f"{selectors[0]} (unknown action: {action})")

    # Drop relationships to media no longer referenced by any picture on this slide,
    # so _prune_unreferenced_parts deletes the orphaned media bytes. This is the
    # de-identification guarantee: a cleared picture's pixels must not survive in
    # the package, only stop rendering.
    remaining_embed_rids = {
        rid for pic in _picture_containers(slide_root) if (rid := _blip_embed_rid(pic))
    }
    for rid in touched_embed_rids:
        if rid in remaining_embed_rids:
            continue
        rel = _find_relationship(rels_root, rid)
        if rel is not None and rel.attrib.get("Type") == IMAGE_REL_TYPE:
            rels_root.remove(rel)

    if errors:
        raise RuntimeError(f"Image edit error(s) on slide {source_slide}: {'; '.join(errors)}")
    return next_media_number
