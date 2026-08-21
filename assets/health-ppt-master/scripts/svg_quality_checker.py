#!/usr/bin/env python3
"""
PPT Master - SVG Quality Check Tool

Checks whether SVG files comply with project technical specifications.

Usage:
    python3 scripts/svg_quality_checker.py <svg_file>
    python3 scripts/svg_quality_checker.py <directory>
    python3 scripts/svg_quality_checker.py --all examples
"""

import sys
import re
import json
import html
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
from xml.etree import ElementTree as ET

try:
    from project_utils import CANVAS_FORMATS
    from error_helper import ErrorHelper
except ImportError:
    print("Warning: Unable to import dependency modules")
    CANVAS_FORMATS = {}
    ErrorHelper = None

try:
    from update_spec import parse_lock as _parse_spec_lock
except ImportError:
    _parse_spec_lock = None  # spec_lock drift check will be skipped

# health-fork: reuse the embedder's exact icon resolver so the checker and the
# finalizer never disagree about which icon names exist. Optional import — the
# icon-availability check is skipped if embed_icons can't be imported.
try:
    from svg_finalize.embed_icons import (
        resolve_icon_path as _resolve_icon_path,
        DEFAULT_ICONS_DIR as _DEFAULT_ICONS_DIR,
    )
except ImportError:
    _resolve_icon_path = None
    _DEFAULT_ICONS_DIR = None

try:
    from svg_to_pptx.animation_config import (
        load_animation_config as _load_animation_config,
        validate_animation_config as _validate_animation_config,
    )
except ImportError:
    _load_animation_config = None
    _validate_animation_config = None


HEX_VALUE_RE = re.compile(r"#[0-9A-Fa-f]{3,8}")
SVG_NS = "http://www.w3.org/2000/svg"

# Ramp envelope for font-size drift detection.
# From design_spec_reference.md §IV — Font Size Hierarchy: the ramp spans
# from page-number floor (0.5x body) to cover-title ceiling (5.0x body).
# Intermediate px values within this envelope are permitted per
# executor-base.md §2.1 ("Executor may use an intermediate size ... provided
# the size's ratio to body falls within the corresponding role's band"); only
# values outside every band — i.e. outside this envelope — are drift.
RAMP_MIN_RATIO = 0.5
RAMP_MAX_RATIO = 5.0


def _font_token_set(stack: str) -> frozenset:
    """Normalize a font-family stack into a set of family tokens (ADR-0050).

    Quoting and inter-token spacing are cosmetic; a stack is fundamentally the
    set of families it names. '"Microsoft YaHei", "微软雅黑", Arial' and
    'Microsoft YaHei, 微软雅黑, Arial' must compare EQUAL so drift detection stops
    flagging identical stacks that merely differ in quotes/spacing.
    """
    return frozenset(
        p.strip().strip('"').strip("'").strip().lower()
        for p in stack.split(",")
        if p.strip().strip('"').strip("'").strip()
    )


def _design_spec_is_brand(spec_path: Path) -> bool:
    """Return True when a design_spec.md frontmatter declares ``kind: brand``.

    Lightweight detector that does not require PyYAML — scans only the
    frontmatter block (``---`` delimited) for a ``kind:`` line whose value
    contains ``brand``. Used by ``check_directory`` to skip SVG validation
    on brand-only template directories.
    """
    try:
        text = spec_path.read_text(encoding='utf-8')
    except OSError:
        return False
    if not text.startswith('---\n'):
        return False
    end = text.find('\n---\n', 4)
    if end == -1:
        return False
    fm_block = text[4:end]
    for line in fm_block.splitlines():
        stripped = line.strip()
        if stripped.startswith('kind:'):
            value = stripped.split(':', 1)[1].strip().strip('"\'')
            return value == 'brand'
    return False


def _parse_placeholders_fallback(block: str) -> Dict[str, Tuple[str, ...]]:
    """Tiny YAML-free reader for the documented ``placeholders:`` shape.

    Used only when PyYAML is unavailable. Recognized lines (indentation-aware,
    two-space indent assumed):

    .. code-block:: yaml

        placeholders:
          01_cover: ["{{TITLE}}", "{{LOGO}}"]
          03_content: []
          03a_content_two_col:
            - "{{LEFT_TITLE}}"
            - "{{RIGHT_TITLE}}"

    Anything outside this minimal grammar is silently skipped — designers who
    rely on advanced YAML should install pyyaml.
    """
    out: Dict[str, Tuple[str, ...]] = {}
    inline_re = re.compile(
        r"^\s{2}([A-Za-z0-9_]+)\s*:\s*\[(.*)\]\s*$"
    )
    empty_re = re.compile(r"^\s{2}([A-Za-z0-9_]+)\s*:\s*\[\s*\]\s*$")
    block_header_re = re.compile(r"^\s{2}([A-Za-z0-9_]+)\s*:\s*$")
    item_re = re.compile(r'^\s{4}-\s*"?([^"]+)"?\s*$')

    in_section = False
    current_block_key: str | None = None
    current_items: List[str] = []

    def _flush_block() -> None:
        nonlocal current_block_key, current_items
        if current_block_key is not None:
            out[current_block_key] = tuple(current_items)
            current_block_key = None
            current_items = []

    for line in block.splitlines():
        if line.startswith("placeholders:"):
            in_section = True
            continue
        if not in_section:
            continue

        # End of section: dedent to a non-key line.
        if line and not line.startswith(" "):
            _flush_block()
            in_section = False
            continue

        if current_block_key is not None:
            m = item_re.match(line)
            if m:
                value = m.group(1).strip().strip('"').strip("'")
                if value:
                    current_items.append(value)
                continue
            # Block ended.
            _flush_block()

        if empty_re.match(line):
            key = empty_re.match(line).group(1)
            out[key] = ()
            continue

        m = inline_re.match(line)
        if m:
            key, raw = m.group(1), m.group(2)
            items = [p.strip().strip('"').strip("'") for p in raw.split(",")]
            out[key] = tuple(item for item in items if item)
            continue

        m = block_header_re.match(line)
        if m:
            current_block_key = m.group(1)
            current_items = []
            continue

    _flush_block()
    return out


class SVGQualityChecker:
    """SVG quality checker"""

    # Default placeholder convention per page-type prefix. This is a *hint*,
    # not a hard contract: templates may define their own placeholder vocabulary
    # via `placeholders:` in design_spec.md frontmatter (see
    # references/template-designer.md §4). Missing default placeholders surface
    # as warnings, never errors — designers may legitimately swap
    # `{{THANK_YOU}}` for `{{CLOSING_MESSAGE}}`, omit `{{DATE}}` when irrelevant,
    # or build content variants with bespoke slot vocabularies.
    #
    # Variants reuse the parent type's expectation (`03a_content_two_col.svg`
    # is matched by the same `03_content` rules as `03_content.svg`).
    DEFAULT_PLACEHOLDER_CONVENTION = {
        "01_cover": ("{{TITLE}}",),  # only the title is universally expected
        "02_chapter": ("{{CHAPTER_TITLE}}",),
        "02_toc": (),  # TOC layouts vary too widely to assert anything
        "03_content": ("{{PAGE_TITLE}}",),
        "04_ending": (),  # ending pages legitimately use varied vocabularies
    }

    def __init__(self, *, template_mode: bool = False):
        self.template_mode = template_mode
        self.results = []
        self.summary = {
            'total': 0,
            'passed': 0,
            'warnings': 0,
            'errors': 0
        }
        self.issue_types = defaultdict(int)
        # spec_lock drift state (populated only when _parse_spec_lock is available
        # and a spec_lock.md is found near the SVG)
        self._lock_cache: Dict[Path, Dict] = {}
        self._drift_summary: Dict[str, Dict[str, set]] = {
            'colors': defaultdict(set),
            'fonts': defaultdict(set),
            'sizes': defaultdict(set),
        }
        self._lock_seen = False  # True once we locate at least one spec_lock.md
        self._source_manifest_cache: Dict[Path, Dict] = {}
        # ADR-0051: deck-level fidelity backstop caches + delivery counters.
        # _extracted_cache: images/image_manifest.json → set of Extracted-original
        #   filenames. _fidelity_cache: images/figure_fidelity.json → verdict ledger.
        self._extracted_cache: Dict[Path, set] = {}
        self._fidelity_cache: Dict[Path, Dict] = {}
        self._letterbox_count = 0       # letterbox issues seen this run (err+warn)
        self._fidelity_total = 0        # Extracted no-crop originals embedded
        self._fidelity_pass = 0         # …of those, with a recorded --verify-crop PASS
        # Template-mode aggregation (populated by check_directory when
        # template_mode=True). Each entry is (severity, kind, message) where
        # severity is 'error' or 'warning'. Printed in print_summary.
        self._template_issues: List[Tuple[str, str, str]] = []
        self._animation_issues: List[Tuple[str, str]] = []

    def check_file(self, svg_file: str, expected_format: str = None) -> Dict:
        """
        Check a single SVG file

        Args:
            svg_file: SVG file path
            expected_format: Expected canvas format (e.g., 'ppt169')

        Returns:
            Check result dictionary
        """
        svg_path = Path(svg_file)

        if not svg_path.exists():
            return {
                'file': str(svg_file),
                'exists': False,
                'errors': ['File does not exist'],
                'warnings': [],
                'passed': False
            }

        result = {
            'file': svg_path.name,
            'path': str(svg_path),
            'exists': True,
            'errors': [],
            'warnings': [],
            'info': {},
            'passed': True
        }

        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 0. Check XML well-formedness — every other check assumes the file
            # is valid XML.  Bail early on failure so the regex-based checks
            # below don't produce misleading errors on a broken document.
            if self._check_xml_well_formed(content, result):
                # 1. Check viewBox
                self._check_viewbox(content, result, expected_format)

                # 2. Check forbidden elements
                self._check_forbidden_elements(content, result)

                # 3. Check fonts
                self._check_fonts(content, result)

                # 4. Check width/height consistency with viewBox
                self._check_dimensions(content, result)

                # 5. Check text wrapping methods
                self._check_text_elements(content, result)

                # 6. Check image references (file existence and resolution)
                self._check_image_references(content, svg_path, result)

                # 6b. health-fork: check every <use data-icon> name resolves to a
                #     real icon in the library. A locked-but-nonexistent name
                #     (the 16/30 audit gap) otherwise leaves an unexpanded
                #     placeholder that renders nothing in the deck.
                self._check_icon_availability(content, result)

                # 7. Check object-level animation anchor quality.
                self._check_animation_group_ids(content, result)

                # 7b. Check <pattern> elements declare a PPTX preset.
                self._check_pattern_fills(content, result)

                # 7c. health-fork (ADR-0051): flag geometry that renders nothing
                #     because it sits entirely outside the viewBox (off-canvas).
                self._check_offcanvas_geometry(content, result)

                # 8. Check spec_lock drift (colors / font-family / font-size).
                #    Templates do not ship a spec_lock.md, so skip in template
                #    mode to avoid noise.
                if not self.template_mode:
                    self._check_spec_lock_drift(content, svg_path, result)

                # 9. Check web-sourced image attribution. Templates don't carry
                #    image_sources.json; skip in template mode.
                if not self.template_mode:
                    self._check_sourced_image_attribution(content, svg_path, result)

            # Determine pass/fail
            result['passed'] = len(result['errors']) == 0

        except Exception as e:
            result['errors'].append(f"Failed to read file: {e}")
            result['passed'] = False

        # Update statistics
        self.summary['total'] += 1
        if result['passed']:
            if result['warnings']:
                self.summary['warnings'] += 1
            else:
                self.summary['passed'] += 1
        else:
            self.summary['errors'] += 1

        # Categorize issue types
        for error in result['errors']:
            self.issue_types[self._categorize_issue(error)] += 1

        self.results.append(result)
        return result

    def _check_xml_well_formed(self, content: str, result: Dict) -> bool:
        """Check that the SVG content parses as well-formed XML.

        SVG is strict XML.  AI-generated decks frequently produce content that
        looks fine in HTML5-tolerant previews but fails strict XML parsing —
        common causes are HTML named entities (&nbsp; &mdash; &copy;…) and
        bare XML reserved characters in text (R&D, error < 5%).  Such pages
        cannot be exported to PPTX, so we surface them here as a hard error
        before any downstream check looks at them.

        Returns True when the document is well-formed; False otherwise.
        """
        try:
            ET.fromstring(content)
            return True
        except ET.ParseError as e:
            result['errors'].append(
                f"Invalid XML: {e} — SVG must be well-formed XML. "
                f"Use raw Unicode for typography (—, ©, →, NBSP); "
                f"escape XML reserved chars as &amp; &lt; &gt; &quot; &apos; "
                f"(see references/shared-standards.md §1)."
            )
            return False

    def _check_viewbox(self, content: str, result: Dict, expected_format: str = None):
        """Check viewBox attribute"""
        viewbox_match = re.search(r'viewBox="([^"]+)"', content)

        if not viewbox_match:
            result['errors'].append("Missing viewBox attribute")
            return

        viewbox = viewbox_match.group(1)
        result['info']['viewbox'] = viewbox

        # Check format
        if not re.match(r'0 0 \d+ \d+', viewbox):
            result['warnings'].append(f"Unusual viewBox format: {viewbox}")

        # Check if it matches expected format
        if expected_format and expected_format in CANVAS_FORMATS:
            expected_viewbox = CANVAS_FORMATS[expected_format]['viewbox']
            if viewbox != expected_viewbox:
                result['errors'].append(
                    f"viewBox mismatch: expected '{expected_viewbox}', got '{viewbox}'"
                )

    def _check_forbidden_elements(self, content: str, result: Dict):
        """Check forbidden elements (blocklist)"""
        content_lower = content.lower()

        # ============================================================
        # Forbidden elements blocklist - PPT incompatible
        # ============================================================

        # Clipping / masking
        # clipPath is allowed on <image> elements and on pptx_to_svg-generated
        # nested crop <svg data-pptx-crop="1"> wrappers. Both map back to
        # DrawingML picture geometry in the native converter.
        if '<clippath' in content_lower:
            # clip-path on non-image elements → error
            clip_on_non_image = re.search(
                r'<(?!image\b)(?!svg\b[^>]*\bdata-pptx-crop\s*=\s*["\']1["\'])\w+[^>]*\bclip-path\s*=',
                content,
                re.IGNORECASE,
            )
            if clip_on_non_image:
                result['errors'].append(
                    "clip-path is only allowed on <image> elements or "
                    "pptx_to_svg crop wrappers — for shapes, draw the target "
                    "shape directly instead of clipping")
            # Check that every clip-path reference has a matching <clipPath> def
            clip_refs = re.findall(r'clip-path\s*=\s*["\']url\(#([^)]+)\)', content)
            for ref_id in clip_refs:
                if f'id="{ref_id}"' not in content and f"id='{ref_id}'" not in content:
                    result['errors'].append(
                        f"clip-path references #{ref_id} but no matching "
                        f"<clipPath id=\"{ref_id}\"> definition found")
        if '<mask' in content_lower:
            result['errors'].append("Detected forbidden <mask> element (PPT does not support SVG masks)")

        # Style system
        if '<style' in content_lower:
            result['errors'].append("Detected forbidden <style> element (use inline attributes instead)")
        if re.search(r'\bclass\s*=', content):
            result['errors'].append("Detected forbidden class attribute (use inline styles instead)")
        # id attribute: only report error when <style> also exists (id is harmful only with CSS selectors)
        # id inside <defs> for linearGradient/filter etc. is required, Inkscape also auto-adds id to elements,
        # standalone id attributes have no impact on PPT export
        if '<style' in content_lower and re.search(r'\bid\s*=', content):
            result['errors'].append(
                "Detected id attribute used with <style> (CSS selectors forbidden, use inline styles instead)"
            )
        if re.search(r'<\?xml-stylesheet\b', content_lower):
            result['errors'].append("Detected forbidden xml-stylesheet (external CSS references forbidden)")
        if re.search(r'<link[^>]*rel\s*=\s*["\']stylesheet["\']', content_lower):
            result['errors'].append("Detected forbidden <link rel=\"stylesheet\"> (external CSS references forbidden)")
        if re.search(r'@import\s+', content_lower):
            result['errors'].append("Detected forbidden @import (external CSS references forbidden)")

        # Structure / nesting
        if '<foreignobject' in content_lower:
            result['errors'].append(
                "Detected forbidden <foreignObject> element (use <tspan> for manual line breaks)")
        has_symbol = '<symbol' in content_lower
        has_use = re.search(r'<use\b', content_lower) is not None
        if has_symbol and has_use:
            result['errors'].append("Detected forbidden <symbol> + <use> complex usage (use basic shapes or simple <use> instead)")
        # marker-start / marker-end are conditionally allowed (see shared-standards.md §1.1).
        # The converter maps qualifying <marker> defs to native DrawingML <a:headEnd>/<a:tailEnd>.
        # We only warn when a marker is used without an obvious <defs> definition in the same file.
        if re.search(r'\bmarker-(?:start|end)\s*=\s*["\']url\(#([^)]+)\)', content_lower):
            if '<marker' not in content_lower:
                result['errors'].append(
                    "Detected marker-start/marker-end referencing a marker id, "
                    "but no <marker> element found in the file")

        # Text / fonts
        if '<textpath' in content_lower:
            result['errors'].append("Detected forbidden <textPath> element (path text is incompatible with PPT)")
        if '@font-face' in content_lower:
            result['errors'].append("Detected forbidden @font-face (use system font stack)")

        # Animation / interaction
        if re.search(r'<animate', content_lower):
            result['errors'].append("Detected forbidden SMIL animation element <animate*> (SVG animations are not exported)")
        if re.search(r'<set\b', content_lower):
            result['errors'].append("Detected forbidden SMIL animation element <set> (SVG animations are not exported)")
        if '<script' in content_lower:
            result['errors'].append("Detected forbidden <script> element (scripts and event handlers forbidden)")
        if re.search(r'\bon\w+\s*=', content):  # onclick, onload etc.
            result['errors'].append("Detected forbidden event attributes (e.g., onclick, onload)")

        # Other discouraged elements
        if '<iframe' in content_lower:
            result['errors'].append("Detected <iframe> element (should not appear in SVG)")
        if re.search(r'rgba\s*\(', content_lower):
            result['errors'].append("Detected forbidden rgba() color (use fill-opacity/stroke-opacity instead)")
        if re.search(r'<g[^>]*\sopacity\s*=', content_lower):
            result['errors'].append("Detected forbidden <g opacity> (set opacity on each child element individually)")
        if re.search(r'<image[^>]*\sopacity\s*=', content_lower):
            result['errors'].append("Detected forbidden <image opacity> (use overlay mask approach)")

    def _check_fonts(self, content: str, result: Dict):
        """Check font usage.

        PPTX stores a single `typeface` per run with no runtime fallback, so every
        stack must END with a cross-platform pre-installed family. See
        strategist.md §g "PPT-safe font discipline".
        """
        font_matches = re.findall(
            r'font-family[:\s]*["\']([^"\']+)["\']', content, re.IGNORECASE)

        if not font_matches:
            return

        result['info']['fonts'] = list(set(font_matches))

        # Pre-installed on Windows + macOS out of the box (plus their direct
        # FONT_FALLBACK_WIN mappings). A stack whose last concrete family is in
        # this set survives the PPTX round-trip on any viewer machine.
        ppt_safe_tail = {
            'microsoft yahei', 'simhei', 'simsun', 'kaiti', 'fangsong',
            'dengxian', 'microsoft jhenghei',
            'pingfang sc', 'heiti sc', 'songti sc', 'stsong',
            'arial', 'arial black', 'calibri', 'segoe ui', 'verdana',
            'helvetica', 'helvetica neue', 'tahoma', 'trebuchet ms',
            'times new roman', 'times', 'georgia', 'cambria', 'palatino',
            'consolas', 'courier new', 'menlo', 'monaco',
            'impact',
        }

        for font_family in font_matches:
            # Drop the generic CSS fallback (sans-serif / serif / monospace)
            # and inspect the last concrete family.
            parts = [p.strip().strip('"').strip("'").lower()
                     for p in font_family.split(',')]
            parts = [p for p in parts
                     if p and p not in ('sans-serif', 'serif', 'monospace',
                                        'cursive', 'fantasy', 'system-ui')]
            if not parts:
                continue
            tail = parts[-1]
            if tail not in ppt_safe_tail:
                result['warnings'].append(
                    f"Font stack does not end on a PPT-safe family "
                    f"(expected e.g. Microsoft YaHei / SimSun / Arial / "
                    f"Times New Roman / Consolas): {font_family}"
                )
                break

    def _check_dimensions(self, content: str, result: Dict):
        """Check width/height consistency with viewBox"""
        width_match = re.search(r'width="(\d+)"', content)
        height_match = re.search(r'height="(\d+)"', content)

        if width_match and height_match:
            width = width_match.group(1)
            height = height_match.group(1)
            result['info']['dimensions'] = f"{width}x{height}"

            # Check consistency with viewBox
            if 'viewbox' in result['info']:
                viewbox_parts = result['info']['viewbox'].split()
                if len(viewbox_parts) == 4:
                    vb_width, vb_height = viewbox_parts[2], viewbox_parts[3]
                    if width != vb_width or height != vb_height:
                        result['warnings'].append(
                            f"width/height ({width}x{height}) does not match viewBox "
                            f"({vb_width}x{vb_height})"
                        )

    def _check_text_elements(self, content: str, result: Dict):
        """Check text elements and wrapping methods"""
        # Count text and tspan elements
        text_count = content.count('<text')
        tspan_count = content.count('<tspan')

        result['info']['text_elements'] = text_count
        result['info']['tspan_elements'] = tspan_count

        # Check for overly long single-line text (may need wrapping)
        text_matches = re.findall(r'<text[^>]*>([^<]{100,})</text>', content)
        if text_matches:
            result['warnings'].append(
                f"Detected {len(text_matches)} potentially overly long single-line text(s) (consider using tspan for wrapping)"
            )

    def _check_image_references(self, content: str, svg_path: Path, result: Dict):
        """Check image file existence and resolution vs display size."""
        # Find all <image ...> elements (capture the full tag)
        img_tag_pattern = re.compile(r'<image\b([^>]*)/?>', re.IGNORECASE)

        svg_dir = svg_path.parent
        checked = set()
        # ADR-0051: Extracted-original filenames (journal_club source figures).
        extracted_set = self._load_extracted_filenames(svg_path)

        for tag_match in img_tag_pattern.finditer(content):
            attrs = tag_match.group(1)

            # Extract href (prefer href over xlink:href). Quote-agnostic: a
            # single-quoted attribute is valid XML and must NOT slip past the
            # image checks (adversarial finding: single quotes bypassed the whole
            # <image> — fidelity gate, existence, letterbox).
            href_match = (
                re.search(r'\bhref\s*=\s*(["\'])(?!data:)(.*?)\1', attrs) or
                re.search(r'\bxlink:href\s*=\s*(["\'])(?!data:)(.*?)\1', attrs)
            )
            if not href_match:
                continue
            href = href_match.group(2)

            # ADR-0051: classify this occurrence BEFORE dedup. is_meet is part of
            # the dedup key so a cropped (slice) embed of a file cannot mask a
            # later no-crop (meet) embed of the SAME file — the fidelity/letterbox
            # gates below are per-crop-mode, not per-filename.
            basename = Path(href).name
            is_source_marked = re.search(
                r'\bdata-fidelity\s*=\s*["\']source["\']', attrs) is not None
            is_extracted = is_source_marked or basename in extracted_set
            par_match = re.search(r'\bpreserveAspectRatio\s*=\s*(["\'])(.*?)\1', attrs)
            par = (par_match.group(2) if par_match else "xMidYMid meet").lower()
            is_meet = "slice" not in par and "none" not in par

            dedup_key = (href, is_meet)
            if dedup_key in checked:
                continue
            checked.add(dedup_key)

            # Resolve path relative to SVG file directory
            img_path = (svg_dir / href).resolve()

            if not img_path.exists():
                result['errors'].append(
                    f"Image file not found: {href} (resolved to {img_path})")
                continue

            # (B) deck-level fidelity backstop: an Extracted original embedded
            # no-crop MUST carry a recorded --verify-crop PASS.
            if is_extracted and is_meet:
                self._check_fidelity_ledger(basename, svg_path, result)

            # Check resolution vs display size (quote-agnostic)
            w_match = re.search(r'\bwidth\s*=\s*(["\'])(.*?)\1', attrs)
            h_match = re.search(r'\bheight\s*=\s*(["\'])(.*?)\1', attrs)
            display_w_str = w_match.group(2) if w_match else None
            display_h_str = h_match.group(2) if h_match else None
            if not display_w_str or not display_h_str:
                continue

            try:
                display_w = float(display_w_str)
                display_h = float(display_h_str)
            except (ValueError, TypeError):
                continue

            try:
                from PIL import Image as PILImage
                with PILImage.open(img_path) as img:
                    actual_w, actual_h = img.size

                if actual_w < display_w or actual_h < display_h:
                    result['warnings'].append(
                        f"Image {href} is {actual_w}x{actual_h} but displayed at "
                        f"{int(display_w)}x{int(display_h)} — may appear blurry")
                elif actual_w > display_w * 4 and actual_h > display_h * 4:
                    result['warnings'].append(
                        f"Image {href} is {actual_w}x{actual_h} but displayed at "
                        f"{int(display_w)}x{int(display_h)} — consider downsizing "
                        f"to reduce file size")

                # Letterbox check (ADR-0050/0051): a no-crop image (preserveAspectRatio
                # "…meet", the SVG default when absent) is centered in its box and
                # letterboxed when the box ratio ≠ the image's native ratio. `slice`/
                # `none` crop or stretch, so a ratio mismatch there is intentional.
                # For an Extracted source original (journal_club evidence) the empty
                # bands are a fidelity/layout defect → ERROR; otherwise a WARNING.
                if is_meet and display_w > 0 and display_h > 0 and actual_h > 0:
                    box_ratio = display_w / display_h
                    native_ratio = actual_w / actual_h
                    if box_ratio > 0 and native_ratio > 0:
                        fill = min(box_ratio, native_ratio) / max(box_ratio, native_ratio)
                        if fill < 0.85:
                            self._letterbox_count += 1
                            detail = (
                                f"box ratio {box_ratio:.2f} "
                                f"(w/h {int(display_w)}x{int(display_h)}) vs image native "
                                f"{native_ratio:.2f} ({actual_w}x{actual_h}) → ~{fill:.0%} fill, "
                                "empty bands. Size the box to the image's native ratio "
                                "(no-crop rule).")
                            if is_extracted:
                                result['errors'].append(
                                    f"Image {href}: letterbox on an Extracted source "
                                    f"original — {detail} This is a journal_club "
                                    "fidelity/layout defect; reflow text/caption around the "
                                    "figure at its native ratio (executor-base.md §6 / "
                                    "ADR-0051).")
                            else:
                                result['warnings'].append(
                                    f"Image {href}: letterbox — {detail} "
                                    "(executor-base.md §6 / ADR-0050)")
            except ImportError:
                pass  # PIL not available, skip resolution check
            except Exception:
                pass  # Image unreadable, skip resolution check

    def _check_icon_availability(self, content: str, result: Dict):
        """health-fork: every <use data-icon="lib/name"> must resolve in the library.

        Reuses embed_icons.resolve_icon_path so the checker's verdict is identical
        to what the finalizer/native converter will actually find. An unresolved
        name is an ERROR (not a warning): it is a broken deliverable — the icon
        renders as nothing — not a style choice. Names are reported with their
        library so a typo is distinguishable from a genuinely-absent brand icon.
        """
        if _resolve_icon_path is None or _DEFAULT_ICONS_DIR is None:
            return  # embed_icons unavailable — skip rather than false-fail
        icons_dir = Path(_DEFAULT_ICONS_DIR)
        # Same element/attr pattern the embedder matches (embed_icons.py §process_svg_file)
        missing = []
        seen = set()
        for icon_name in re.findall(r'<use\s+[^>]*data-icon="([^"]+)"[^>]*/?>', content):
            if icon_name in seen:
                continue
            seen.add(icon_name)
            try:
                icon_path, _ = _resolve_icon_path(icon_name, icons_dir)
            except Exception:
                missing.append(icon_name)
                continue
            if not icon_path.exists():
                missing.append(icon_name)
        for icon_name in missing:
            result['errors'].append(
                f"Icon not found in library: '{icon_name}' "
                f"(no such file under templates/icons/) — pick a name that exists "
                f"(ls templates/icons/<library>/ | grep <keyword>) or this <use> "
                f"renders nothing"
            )

    def _find_images_dir(self, svg_path: Path) -> Path | None:
        """Locate the project's images/ dir for a project SVG (ADR-0051).

        Mirrors _find_image_sources_manifest: quality checks run on svg_output/*.svg
        but the check must also work from project root or svg_final/.
        """
        for base in (svg_path.parent, svg_path.parent.parent,
                     svg_path.parent.parent.parent):
            candidate = base / 'images'
            if candidate.is_dir():
                return candidate
        return None

    def _load_extracted_filenames(self, svg_path: Path) -> set:
        """Set of Extracted-original filenames from images/image_manifest.json.

        The manifest is a JSON LIST of dicts (document-parser / project_manager
        shape); each `filename` is a source figure/table raster extracted verbatim
        from the paper. Empty set when there is no manifest (non-journal_club decks,
        single-file checks) → the fidelity gate then imposes no requirement.
        """
        images_dir = self._find_images_dir(svg_path)
        if images_dir is None:
            return set()
        manifest = images_dir / 'image_manifest.json'
        if manifest in self._extracted_cache:
            return self._extracted_cache[manifest]
        names: set = set()
        try:
            data = json.loads(manifest.read_text(encoding='utf-8'))
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and isinstance(item.get('filename'), str):
                        names.add(item['filename'])
        except (OSError, json.JSONDecodeError):
            pass
        self._extracted_cache[manifest] = names
        return names

    def _load_fidelity_ledger(self, svg_path: Path) -> Dict:
        """The images/figure_fidelity.json verdict ledger (ADR-0051 A), written by
        render_pdf_region.py --verify-crop --record. dict keyed by embedded asset
        filename → {verdict, coverage, …}. Empty dict when absent."""
        images_dir = self._find_images_dir(svg_path)
        if images_dir is None:
            return {}
        ledger_path = images_dir / 'figure_fidelity.json'
        if ledger_path in self._fidelity_cache:
            return self._fidelity_cache[ledger_path]
        ledger: Dict = {}
        try:
            loaded = json.loads(ledger_path.read_text(encoding='utf-8'))
            if isinstance(loaded, dict):
                ledger = loaded
        except (OSError, json.JSONDecodeError):
            pass
        self._fidelity_cache[ledger_path] = ledger
        return ledger

    def _check_fidelity_ledger(self, basename: str, svg_path: Path, result: Dict):
        """Deck-level fidelity backstop (ADR-0051 B): an Extracted source figure
        embedded no-crop MUST have a recorded --verify-crop PASS.

        This turns ADR-0050's per-figure gate from an honor-system checkbox into an
        enforced contract — a model that skips --verify-crop, or ships a FRAGMENT,
        fails the QC gate (and therefore the export gate) instead of silently
        shipping a legend sliver / partial figure (real defect: P5 Figure-3).
        """
        self._fidelity_total += 1
        ledger = self._load_fidelity_ledger(svg_path)
        entry = ledger.get(basename)
        if entry is None:
            result['errors'].append(
                f"Extracted source figure '{basename}' embedded (no-crop) but has NO "
                f"--verify-crop PASS in images/figure_fidelity.json — the per-figure "
                f"fidelity gate did not run for it. Run: render_pdf_region.py "
                f"--verify-crop --bbox … --frac --caption \"Figure N\" "
                f"--record images/figure_fidelity.json --asset {basename}  (re-crop via "
                f"--detect-figure until PASS) before embedding (ADR-0050/0051)."
            )
            return
        verdict = entry.get('verdict')
        if verdict != 'PASS':
            result['errors'].append(
                f"Extracted source figure '{basename}' has --verify-crop verdict "
                f"'{verdict}' (coverage {entry.get('coverage')}), not PASS — it is a "
                f"partial/fragment crop, not the complete figure. Re-crop with the "
                f"--detect-figure coords and re-verify until PASS (ADR-0051)."
            )
            return
        self._fidelity_pass += 1

    @staticmethod
    def _elem_geom_box(elem) -> Tuple[float, float, float, float] | None:
        """Absolute box (x0,y0,x1,y1) for a rect/image with numeric geometry, or None.

        Missing x/y default to 0 (SVG default); width/height must be present, numeric
        and positive. Non-numeric units (%, em) → None (can't place → skip)."""
        def _num(name: str, default=None):
            v = elem.get(name)
            if v is None:
                return default
            v = v.strip()
            if v.endswith('px'):
                v = v[:-2].strip()
            try:
                return float(v)
            except ValueError:
                return None
        x = _num('x', 0.0)
        y = _num('y', 0.0)
        w = _num('width')
        h = _num('height')
        if x is None or y is None or w is None or h is None:
            return None
        if w <= 0 or h <= 0:
            return None
        return (x, y, x + w, y + h)

    # Coordinate-space containers whose children are NOT laid out against the page
    # viewBox (defs templates, clip geometry, tiling patterns, and NESTED <svg>
    # which establishes its own viewport/viewBox) — never off-canvas relative to
    # the page. `svg` is safe here because _walk starts on the ROOT svg's children,
    # so only genuine nested <svg> subtrees are skipped.
    _OFFCANVAS_SKIP = {'defs', 'symbol', 'clipPath', 'mask', 'pattern', 'marker', 'svg'}

    def _check_offcanvas_geometry(self, content: str, result: Dict):
        """Flag <image>/<rect> that sit ENTIRELY outside the viewBox (ADR-0051 D).

        Such an element renders nothing — a silent content loss. Conservative by
        design to keep false positives ≈ 0: only elements with NO transform anywhere
        in their ancestry (transforms could bring them on-canvas — we can't cheaply
        resolve them, so we skip) and only the unambiguous "zero intersection with
        the viewBox" case. An off-canvas <image> is a lost figure → ERROR; other
        shapes may be intentional bleed → WARNING.
        """
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return
        vb = root.get('viewBox')
        if not vb:
            return
        # viewBox values may be separated by whitespace OR commas (both spec-valid,
        # e.g. "0, 0, 1280, 720") — split on either so a comma form doesn't silently
        # disable the gate.
        parts = re.split(r'[\s,]+', vb.strip())
        if len(parts) != 4:
            return
        try:
            vx, vy, vw, vh = (float(p) for p in parts)
        except ValueError:
            return
        if vw <= 0 or vh <= 0:
            return
        vx1, vy1 = vx + vw, vy + vh

        def _walk(elem, has_tf: bool):
            tag = elem.tag.split('}', 1)[-1]
            if tag in self._OFFCANVAS_SKIP:
                return  # skip the whole subtree — different coordinate space
            tf = has_tf or (elem.get('transform') is not None)
            if tag in ('image', 'rect') and not tf:
                box = self._elem_geom_box(elem)
                if box is not None:
                    ex0, ey0, ex1, ey1 = box
                    outside = (ex1 <= vx or ex0 >= vx1 or ey1 <= vy or ey0 >= vy1)
                    if outside:
                        loc = f"x={ex0:.0f} y={ey0:.0f} w={ex1 - ex0:.0f} h={ey1 - ey0:.0f}"
                        if tag == 'image':
                            result['errors'].append(
                                f"<image> ({loc}) is entirely outside the viewBox "
                                f"({vw:.0f}x{vh:.0f}) — it renders nothing (off-canvas). "
                                f"Reposition it inside 0,0..{vw:.0f},{vh:.0f}."
                            )
                        else:
                            result['warnings'].append(
                                f"<{tag}> ({loc}) is entirely outside the viewBox "
                                f"({vw:.0f}x{vh:.0f}) — renders nothing; ignore only if "
                                f"this is intentional off-canvas bleed."
                            )
            for child in list(elem):
                _walk(child, tf)

        for child in list(root):
            _walk(child, root.get('transform') is not None)

    def _check_animation_group_ids(self, content: str, result: Dict):
        """Warn when visible top-level groups cannot be customized."""
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return

        non_visual = {'defs', 'title', 'desc', 'metadata', 'style'}
        for index, child in enumerate(list(root), start=1):
            tag = child.tag.split('}', 1)[-1]
            if tag in non_visual:
                continue
            if tag == 'g' and not child.get('id'):
                result['warnings'].append(
                    f"Top-level visible <g> #{index} has no id; "
                    "object-level animation config cannot reference it"
                )

    # OOXML ST_PresetPatternVal enum — anything outside this set produces a
    # PPTX schema violation ("PowerPoint found a problem with the content").
    _OOXML_PATTERN_PRESETS = frozenset({
        'pct5', 'pct10', 'pct20', 'pct25', 'pct30', 'pct40', 'pct50', 'pct60',
        'pct70', 'pct75', 'pct80', 'pct90',
        'horz', 'vert', 'ltHorz', 'ltVert', 'dkHorz', 'dkVert',
        'narHorz', 'narVert', 'dashHorz', 'dashVert',
        'cross', 'dnDiag', 'upDiag', 'ltDnDiag', 'ltUpDiag', 'dkDnDiag',
        'dkUpDiag', 'wdDnDiag', 'wdUpDiag',
        'dashDnDiag', 'dashUpDiag', 'diagCross',
        'smCheck', 'lgCheck', 'smGrid', 'lgGrid', 'dotGrid', 'smConfetti',
        'lgConfetti', 'horzBrick', 'diagBrick', 'solidDmnd', 'openDmnd',
        'dotDmnd', 'plaid', 'sphere', 'weave', 'wave', 'trellis', 'zigZag',
        'divot', 'shingle',
    })

    def _check_pattern_fills(self, content: str, result: Dict):
        """Audit <pattern> defs that drive PPTX <a:pattFill> output.

        svg_to_pptx maps <pattern fill> to native <a:pattFill prst="...">. The
        preset name comes from `data-pptx-pattern` (e.g. `lgGrid` / `smGrid` /
        `dkUpDiag`). Two failure modes worth catching pre-export:

        1. Missing annotation → converter silently falls back to `ltUpDiag`
           (diagonal stripes) and picks `bg = #FFFFFF` when the pattern has
           no child <rect>, turning a hand-authored grid into white-on-stripes
           in PPTX.
        2. Invalid preset name → PPTX schema rejects the file; PowerPoint
           opens it with "needs to be repaired". OOXML
           `ST_PresetPatternVal` is a closed enum — only the names in
           `_OOXML_PATTERN_PRESETS` are legal. Inventing `ltGrid` (no such
           value) is the canonical mistake; the only grids are `smGrid` /
           `lgGrid` / `dotGrid`.
        """
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return

        for pattern in root.iter(f'{{{SVG_NS}}}pattern'):
            pat_id = pattern.get('id', '<unnamed>')
            prst = pattern.get('data-pptx-pattern')
            if not prst:
                result['warnings'].append(
                    f"<pattern id=\"{pat_id}\"> has no data-pptx-pattern attribute — "
                    "PPTX export will fall back to `ltUpDiag` (diagonal stripes), "
                    "not your custom geometry. Add data-pptx-pattern=\"lgGrid\" / "
                    "\"smGrid\" / etc. plus a <rect fill=\"<bg>\"/> child so the "
                    "preset and bg color match your design."
                )
                continue
            if prst not in self._OOXML_PATTERN_PRESETS:
                result['errors'].append(
                    f"<pattern id=\"{pat_id}\"> uses data-pptx-pattern=\"{prst}\" "
                    "which is not in OOXML ST_PresetPatternVal — exported PPTX "
                    "will fail schema validation ('needs to be repaired'). "
                    "Use one of: smGrid / lgGrid / dotGrid (grids), "
                    "ltUpDiag / dkUpDiag / cross / diagCross / weave / plaid / "
                    "horzBrick (others); full enum in svg_quality_checker.py "
                    "_OOXML_PATTERN_PRESETS."
                )

    def _get_spec_lock(self, svg_path: Path):
        """Locate and parse spec_lock.md near the SVG. Returns dict or None.

        Looks in svg_path.parent and svg_path.parent.parent (covers the two
        common layouts: SVG directly under <project>/ or under
        <project>/svg_output/). Results are cached per lock path.
        """
        if _parse_spec_lock is None:
            return None
        for candidate in (svg_path.parent / 'spec_lock.md',
                          svg_path.parent.parent / 'spec_lock.md'):
            if candidate in self._lock_cache:
                return self._lock_cache[candidate]
            if candidate.exists():
                try:
                    data = _parse_spec_lock(candidate)
                except Exception:
                    data = None
                self._lock_cache[candidate] = data
                if data is not None:
                    self._lock_seen = True
                return data
        return None

    def _check_spec_lock_drift(self, content: str, svg_path: Path, result: Dict):
        """Detect values used in the SVG that fall outside spec_lock.md.

        Covers colors (fill / stroke / stop-color), font-family, and font-size.
        Emits per-file warnings summarising the drift counts; exact drifting
        values are accumulated in self._drift_summary for the end-of-run
        aggregation. When spec_lock.md is missing, silently skip (consistent
        with executor-base.md §2.1's 'missing lock → warn and proceed' policy).
        """
        lock = self._get_spec_lock(svg_path)
        if lock is None:
            return

        # Build allow-sets from the lock
        allowed_colors = set()
        for v in lock.get('colors', {}).values():
            if HEX_VALUE_RE.fullmatch(v):
                allowed_colors.add(v.upper())

        typo = lock.get('typography', {})
        # Font families: default `font_family` plus any per-role `*_family`
        # override (title_family / body_family / emphasis_family / code_family,
        # per spec_lock_reference.md). Any of these is a legitimate declared
        # value; an SVG that uses any one of them is not drifting.
        #
        # Compare NORMALIZED (ADR-0050): a font-family stack is a comma list of
        # families; quoting and inter-token spacing are cosmetic and vary freely
        # between spec_lock ('"Microsoft YaHei", "微软雅黑", …') and the SVG
        # (Microsoft YaHei, 微软雅黑, …). The old verbatim string compare flagged
        # these identical stacks as drift → wasted patch loops. We now compare the
        # SET of family tokens and treat "SVG families ⊆ any declared stack" as
        # no-drift (a subset is fine — the SVG may drop a fallback like PingFang).
        allowed_font_token_sets = []  # list[frozenset[str]] — one per declared stack
        if typo:
            for k, v in typo.items():
                if k != 'font_family' and not k.endswith('_family'):
                    continue
                v_clean = v.strip()
                if not v_clean or v_clean.lower().startswith('same as'):
                    continue
                allowed_font_token_sets.append(_font_token_set(v_clean))

        # Sizes: declared slots are anchors; body is the ramp baseline.
        allowed_sizes = set()
        body_px = None
        for k, v in typo.items():
            if k == 'font_family' or k.endswith('_family'):
                continue
            allowed_sizes.add(self._normalize_size(v))
            if k == 'body':
                try:
                    body_px = float(self._normalize_size(v))
                except (ValueError, TypeError):
                    body_px = None

        # Scan SVG for used values
        color_drifts = set()
        for attr in ('fill', 'stroke', 'stop-color'):
            pattern = re.compile(rf'\b{attr}\s*=\s*["\'](#[0-9A-Fa-f]{{3,8}})["\']')
            for m in pattern.finditer(content):
                val = m.group(1).upper()
                if val not in allowed_colors:
                    color_drifts.add(val)

        font_drifts = set()
        for m in re.finditer(r'font-family\s*=\s*["\']([^"\']+)["\']', content):
            val = m.group(1).strip()
            if not allowed_font_token_sets:
                continue
            used = _font_token_set(val)
            # No drift if the SVG's families are a subset of ANY declared stack
            # (normalized: quotes/spacing ignored; dropping a fallback is fine).
            if any(used <= allowed for allowed in allowed_font_token_sets):
                continue
            font_drifts.add(val)

        size_drifts = set()
        for m in re.finditer(r'font-size\s*=\s*["\']([^"\']+)["\']', content):
            val = self._normalize_size(m.group(1))
            if not allowed_sizes or val in allowed_sizes:
                continue
            # Intermediate values are allowed when they sit inside the ramp
            # envelope (ratio to body within [RAMP_MIN_RATIO, RAMP_MAX_RATIO]).
            if body_px and body_px > 0:
                try:
                    ratio = float(val) / body_px
                    if RAMP_MIN_RATIO <= ratio <= RAMP_MAX_RATIO:
                        continue
                except ValueError:
                    pass
            size_drifts.add(val)

        # Record in run-wide aggregation
        fname = svg_path.name
        for v in color_drifts:
            self._drift_summary['colors'][v].add(fname)
        for v in font_drifts:
            self._drift_summary['fonts'][v].add(fname)
        for v in size_drifts:
            self._drift_summary['sizes'][v].add(fname)

        # Per-file warning (one condensed line; details live in summary)
        parts = []
        if color_drifts:
            parts.append(f"{len(color_drifts)} color(s)")
        if font_drifts:
            parts.append(f"{len(font_drifts)} font-family value(s)")
        if size_drifts:
            parts.append(f"{len(size_drifts)} font-size value(s)")
        if parts:
            result['warnings'].append(
                f"spec_lock drift: {', '.join(parts)} not in spec_lock.md "
                "(see drift summary for details)"
            )

    def _find_image_sources_manifest(self, svg_path: Path) -> Path | None:
        """Locate image_sources.json for a project SVG.

        Quality checks run primarily on <project>/svg_output/*.svg, but this
        also supports SVGs checked from project root or svg_final.
        """
        bases = (svg_path.parent, svg_path.parent.parent, svg_path.parent.parent.parent)
        for base in bases:
            candidate = base / 'images' / 'image_sources.json'
            if candidate.exists():
                return candidate
        return None

    def _load_image_sources_manifest(self, svg_path: Path) -> Dict:
        manifest_path = self._find_image_sources_manifest(svg_path)
        if manifest_path is None:
            return {}
        if manifest_path in self._source_manifest_cache:
            return self._source_manifest_cache[manifest_path]
        try:
            payload = json.loads(manifest_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            payload = {}
        self._source_manifest_cache[manifest_path] = payload
        return payload

    def _check_sourced_image_attribution(self, content: str, svg_path: Path, result: Dict):
        """Require visible credit text for attribution-required web images.

        image_search.py records the legal tier in images/image_sources.json;
        Executor must render compact credit text into the SVG. This check
        prevents a quality-first CC BY / CC BY-SA image from silently reaching
        export without attribution.
        """
        manifest = self._load_image_sources_manifest(svg_path)
        items = manifest.get('items') or []
        if not items:
            return

        text_content = html.unescape(re.sub(r'<[^>]+>', ' ', content))
        text_content = re.sub(r'\s+', ' ', text_content)
        svg_stem = svg_path.stem

        for item in items:
            if not item.get('attribution_required') and item.get('license_tier') != 'attribution-required':
                continue

            filename = Path(str(item.get('filename') or '')).name
            slide = str(item.get('slide') or '').strip()
            referenced = bool(filename and filename in content)
            same_slide = bool(slide and slide == svg_stem)
            if not referenced and not same_slide:
                continue

            license_name = str(item.get('license_name') or '').upper()
            license_token = 'CC BY-SA' if 'BY-SA' in license_name else 'CC BY'
            has_credit = license_token in text_content.upper()
            if not has_credit:
                result['errors'].append(
                    f"Missing inline attribution for sourced image {filename or '(unknown)'} "
                    f"({license_token}). Add compact credit text per "
                    f"references/image-searcher.md §7."
                )

    @staticmethod
    def _normalize_size(value: str) -> str:
        """Normalize a font-size value for comparison: lowercase, strip spaces,
        strip trailing 'px'. Other units (em / rem / %) are kept as-is so that
        e.g. '1.5em' vs '24' stay distinct."""
        v = value.strip().lower()
        if v.endswith('px'):
            v = v[:-2].strip()
        return v

    def _categorize_issue(self, error_msg: str) -> str:
        """Categorize issue type"""
        if 'Invalid XML' in error_msg:
            return 'XML well-formedness'
        elif 'viewBox' in error_msg:
            return 'viewBox issues'
        elif 'foreignObject' in error_msg:
            return 'foreignObject'
        elif 'font' in error_msg.lower():
            return 'Font issues'
        else:
            return 'Other'

    def check_directory(self, directory: str, expected_format: str = None) -> List[Dict]:
        """
        Check all SVG files in a directory

        Args:
            directory: Directory path
            expected_format: Expected canvas format

        Returns:
            List of check results
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            print(f"[ERROR] Directory does not exist: {directory}")
            return []

        # Brand-only template directories (templates/brands/<id>/) have no SVG
        # roster — design_spec.md frontmatter declares `kind: brand`. Skip SVG
        # checks entirely; brand validation lives in register_template.py.
        if self.template_mode and dir_path.is_dir():
            spec = dir_path / 'design_spec.md'
            if spec.exists() and _design_spec_is_brand(spec):
                print(
                    f"[INFO] Brand directory detected (kind: brand) — "
                    f"SVG checks skipped."
                )
                print(
                    f"[INFO] Validate brand specs via: "
                    f"python3 scripts/register_template.py "
                    f"--kind brand <brand_id> --dry-run"
                )
                return self.results

        # Find all SVG files
        if dir_path.is_file():
            svg_files = [dir_path]
        else:
            if self.template_mode:
                # Template directories live at templates/{layouts,decks}/<id>/.
                svg_files = sorted(dir_path.glob('*.svg'))
            else:
                svg_output = dir_path / \
                    'svg_output' if (
                        dir_path / 'svg_output').exists() else dir_path
                svg_files = sorted(svg_output.glob('*.svg'))

        if not svg_files:
            print(f"[WARN] No SVG files found")
            return []

        print(f"\n[SCAN] Checking {len(svg_files)} SVG file(s)...\n")

        for svg_file in svg_files:
            result = self.check_file(str(svg_file), expected_format)
            self._print_result(result)

        if self.template_mode and dir_path.is_dir():
            self._check_template_contract(dir_path, svg_files)
        elif dir_path.is_dir():
            self._check_animation_config_contract(dir_path)

        return self.results

    def _check_animation_config_contract(self, dir_path: Path) -> None:
        """Project-level animations.json reference checks."""
        if _load_animation_config is None or _validate_animation_config is None:
            return
        project_path = dir_path if (dir_path / 'svg_output').exists() else dir_path.parent
        try:
            config = _load_animation_config(project_path)
        except Exception as exc:
            self._animation_issues.append(('error', f"animations.json is invalid: {exc}"))
            return
        if not config:
            return
        for warning in _validate_animation_config(project_path, config):
            self._animation_issues.append(('warning', warning))

    def _check_template_contract(self, dir_path: Path,
                                 svg_files: List[Path]) -> None:
        """Template-mode-only checks: roster ↔ design_spec consistency and
        per-page placeholder hints.

        - **Roster mismatch (orphan / missing)** is reported as an *error*: a
          stale roster will produce a wrong ``layouts_index.json`` entry.
        - **Placeholder gaps** are reported as *warnings*. Templates may
          legitimately omit conventional placeholders or swap them out (e.g.
          ``{{CLOSING_MESSAGE}}`` instead of ``{{THANK_YOU}}``), and a content
          variant may use a bespoke slot vocabulary. Designers can declare
          their own per-stem expectations via ``placeholders:`` frontmatter
          in ``design_spec.md`` to suppress these warnings explicitly.

        Issues are aggregated and printed in :py:meth:`print_summary` so the
        per-file report stays focused on intrinsic SVG validity.
        """
        spec_path = dir_path / 'design_spec.md'
        spec_text = spec_path.read_text(encoding='utf-8') if spec_path.exists() else ""
        spec_pages = self._extract_spec_roster(spec_text) if spec_text else []
        custom_contract = self._extract_frontmatter_placeholders(spec_text) if spec_text else {}

        on_disk = {p.stem for p in svg_files}

        if spec_pages:
            spec_set = set(spec_pages)
            orphan = sorted(on_disk - spec_set)
            missing = sorted(spec_set - on_disk)
            for page in orphan:
                self._template_issues.append((
                    'error',
                    'roster_orphan',
                    f"{page}.svg exists on disk but is not listed in design_spec.md Page Roster",
                ))
            for page in missing:
                self._template_issues.append((
                    'error',
                    'roster_missing',
                    f"design_spec.md Page Roster lists {page} but {page}.svg is missing on disk",
                ))
        elif spec_path.exists():
            # design_spec.md is present but the roster parser found nothing —
            # surface as a warning. Legacy specs may lack an explicit roster.
            self._template_issues.append((
                'warning',
                'roster_unknown',
                f"could not extract page roster from {spec_path.name}; "
                "skipping orphan/missing checks",
            ))
        else:
            self._template_issues.append((
                'error',
                'spec_missing',
                f"{spec_path.name} not found — required for every library template",
            ))

        # Per-file placeholder coverage. Variants reuse the parent type's set
        # (e.g. 03a_content_two_col.svg ↔ 03_content rules) unless the spec
        # frontmatter overrides that page (custom_contract takes precedence).
        for svg_file in svg_files:
            expected = self._lookup_template_contract(
                svg_file.stem, overrides=custom_contract,
            )
            if expected is None:
                continue  # extension pages or stems with no convention
            try:
                content = svg_file.read_text(encoding='utf-8')
            except OSError:
                continue
            for placeholder in expected:
                if placeholder not in content:
                    self._template_issues.append((
                        'warning',
                        'placeholder_hint',
                        f"{svg_file.name}: missing conventional placeholder {placeholder} "
                        "(declare 'placeholders:' frontmatter in design_spec.md to silence)",
                    ))

    @staticmethod
    def _extract_frontmatter_placeholders(spec_text: str) -> Dict[str, Tuple[str, ...]]:
        """Read the optional ``placeholders:`` map from design_spec.md frontmatter.

        Shape:

        .. code-block:: yaml

            placeholders:
              01_cover: ["{{TITLE}}", "{{BRAND_LOGO}}"]
              03_content: []        # explicitly assert "no expectation"
              03a_content_two_col:  # variant-specific override
                - "{{LEFT_TITLE}}"
                - "{{RIGHT_TITLE}}"

        Each key is a stem (full filename without ``.svg``) or page-type prefix
        (``01_cover``). An empty list silences the default convention for that
        stem; a populated list replaces the default. Stems / prefixes not
        listed fall back to ``DEFAULT_PLACEHOLDER_CONVENTION``.

        We parse with PyYAML when available; otherwise we fall back to a
        minimal regex that handles the documented shape.
        """
        if not spec_text.startswith("---\n"):
            return {}
        end = spec_text.find("\n---\n", 4)
        if end == -1:
            return {}
        block = spec_text[4:end]

        try:
            import yaml  # type: ignore
        except ImportError:
            return _parse_placeholders_fallback(block)

        try:
            data = yaml.safe_load(block) or {}
        except yaml.YAMLError:
            return {}
        if not isinstance(data, dict):
            return {}
        raw = data.get("placeholders")
        if not isinstance(raw, dict):
            return {}

        out: Dict[str, Tuple[str, ...]] = {}
        for stem, value in raw.items():
            if not isinstance(stem, str):
                continue
            if isinstance(value, list):
                out[stem] = tuple(str(v) for v in value)
            elif value is None:
                out[stem] = ()
        return out

    @staticmethod
    def _extract_spec_roster(spec_text: str) -> List[str]:
        """Best-effort: extract the page roster from design_spec.md.

        Templates do not share a uniform section index for the roster — the
        personality-only skeleton puts it at §V "Page Roster"; legacy specs use
        §VI "Page Roster" or bury filenames under §VII "Page Types" as
        ``### N. Cover Page (01_cover.svg)``. We match by title (any roman
        index), then fall back to scanning the whole document for any
        backtick-wrapped ``<stem>.svg`` reference.

        Returns the deduplicated stem list in document order. Empty result
        means we can't determine the roster confidently — caller should treat
        that as "skip orphan/missing checks", not as "no pages declared".
        """
        # Pass 1: explicit roster section, any roman numeral.
        section = re.search(
            r"^##\s+[IVX]+\.\s+(?:Page Roster|Page Structure|Pages|Page Types)\b.*?(?=^##\s+|\Z)",
            spec_text,
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )
        scope = section.group(0) if section else None

        # Pass 2: full document. We *only* trust this scan when the explicit
        # roster scan came up empty (no `<stem>.svg` references inside it) —
        # otherwise the explicit section's deliberate roster wins over loose
        # mentions elsewhere.
        if scope and re.search(r"[`\(][0-9A-Za-z_]+\.svg[`\)]", scope):
            text = scope
        else:
            text = spec_text

        stems: List[str] = []
        seen: set = set()
        # Accept backtick-quoted (`01_cover.svg`) and parenthesized
        # (01_cover.svg) forms — existing specs use either.
        svg_ref_re = re.compile(r"[`\(]([0-9A-Za-z_]+\.svg)[`\)]")
        for match in svg_ref_re.finditer(text):
            stem = match.group(1)[:-4]
            if stem in seen or not re.match(r"^\d", stem):
                continue
            seen.add(stem)
            stems.append(stem)

        # If the explicit §VI scan listed bare stems (without .svg), accept
        # those as fallback — but only when they were inside that section.
        if not stems and scope:
            for match in re.finditer(r"`([0-9]{2}[a-z]?_[A-Za-z0-9_]+)`", scope):
                stem = match.group(1)
                if stem in seen:
                    continue
                seen.add(stem)
                stems.append(stem)

        return stems

    @classmethod
    def _lookup_template_contract(
        cls, stem: str, *,
        overrides: Dict[str, Tuple[str, ...]] | None = None,
    ) -> Tuple[str, ...] | None:
        """Resolve a SVG stem to its expected placeholder set.

        Resolution order, first hit wins:
        1. ``overrides[stem]`` — frontmatter entry for the exact filename
        2. ``overrides[<page_type_prefix>]`` — frontmatter entry for the
           variant's parent type (e.g. ``03_content`` for
           ``03a_content_two_col``)
        3. ``DEFAULT_PLACEHOLDER_CONVENTION[<page_type_prefix>]``

        Returns ``None`` for stems with no matching convention or override —
        e.g. extension pages like ``05_section_break``. ``()`` (empty tuple)
        is a valid value meaning "no expected placeholders" — used to
        explicitly silence the default convention.
        """
        overrides = overrides or {}
        if stem in overrides:
            return overrides[stem]

        # Variant convention: <NN><letter>?_<rest>; strip the letter to find
        # the parent type prefix, e.g. "03a_content_two_col" -> "03_content".
        match = re.match(r"^(\d{2})([a-z])?_([a-z]+)", stem)
        if not match:
            return None
        num, _letter, kind = match.groups()
        key = f"{num}_{kind}"
        if key in overrides:
            return overrides[key]
        return cls.DEFAULT_PLACEHOLDER_CONVENTION.get(key)

    def _print_result(self, result: Dict):
        """Print check result for a single file"""
        if result['passed']:
            if result['warnings']:
                icon = "[WARN]"
                status = "Passed (with warnings)"
            else:
                icon = "[OK]"
                status = "Passed"
        else:
            icon = "[ERROR]"
            status = "Failed"

        print(f"{icon} {result['file']} - {status}")

        # Display basic info
        if result['info']:
            info_items = []
            if 'viewbox' in result['info']:
                info_items.append(f"viewBox: {result['info']['viewbox']}")
            if info_items:
                print(f"   {' | '.join(info_items)}")

        # Display errors
        if result['errors']:
            for error in result['errors']:
                print(f"   [ERROR] {error}")

        # Display warnings
        if result['warnings']:
            for warning in result['warnings'][:2]:  # Only show first 2 warnings
                print(f"   [WARN] {warning}")
            if len(result['warnings']) > 2:
                print(f"   ... and {len(result['warnings']) - 2} more warning(s)")

        print()

    def print_summary(self):
        """Print check summary"""
        print("=" * 80)
        print("[SUMMARY] Check Summary")
        print("=" * 80)

        print(f"\nTotal files: {self.summary['total']}")
        print(
            f"  [OK] Fully passed: {self.summary['passed']} ({self._percentage(self.summary['passed'])}%)")
        print(
            f"  [WARN] With warnings: {self.summary['warnings']} ({self._percentage(self.summary['warnings'])}%)")
        print(
            f"  [ERROR] With errors: {self.summary['errors']} ({self._percentage(self.summary['errors'])}%)")

        if self.issue_types:
            print(f"\nIssue categories:")
            for issue_type, count in sorted(self.issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {issue_type}: {count}")

        # spec_lock drift aggregation (only printed when a lock was found)
        self._print_drift_summary()

        # Template-mode aggregation (orphan/missing roster + placeholder hints)
        self._print_template_summary()

        # Animation config aggregation.
        self._print_animation_summary()

        # Fix suggestions
        if self.summary['errors'] > 0 or self.summary['warnings'] > 0:
            print(f"\n[TIP] Common fixes:")
            print(f"  1. XML well-formedness: write typography as raw Unicode (—, ©, →, NBSP); escape XML reserved chars as &amp; &lt; &gt; &quot; &apos; — never use HTML named entities like &nbsp; &mdash; &copy;")
            print(f"  2. viewBox issues: Ensure consistency with canvas format (see references/canvas-formats.md)")
            print(f"  3. foreignObject: Use <text> + <tspan> for manual line breaks")
            print(f"  4. Font issues: end every font-family stack with a PPT-safe family (e.g. Microsoft YaHei / Arial / Consolas)")

        # Delivery-honesty fact source (ADR-0051 F): a single machine-computed line
        # the delivery message copies verbatim, so "verified" claims match reality.
        if not self.template_mode:
            if self._fidelity_total:
                fig = (f"{self._fidelity_pass}/{self._fidelity_total} Extracted "
                       "originals --verify-crop PASS")
            else:
                fig = "no Extracted originals"
            print("\n" + "=" * 80)
            print(
                f"[DELIVERY] QC errors={self.summary['errors']} "
                f"warnings={self.summary['warnings']} | "
                f"letterbox={self._letterbox_count} | figures: {fig}"
            )
            print(
                "Copy this line into the delivery message; do NOT claim 'verified' "
                "beyond what it shows (ADR-0050/0051 delivery honesty)."
            )

    def _print_animation_summary(self):
        """Print animations.json validation issues if present."""
        if not self._animation_issues:
            return

        errors = [item for item in self._animation_issues if item[0] == 'error']
        warnings = [item for item in self._animation_issues if item[0] == 'warning']
        self.summary['errors'] += len(errors)
        self.summary['warnings'] += len(warnings)
        for severity, _msg in self._animation_issues:
            self.issue_types[f'animation_config_{severity}'] += 1

        print("\n[ANIMATION] animations.json checks")
        for _severity, msg in errors:
            print(f"  [ERROR] {msg}")
        for _severity, msg in warnings:
            print(f"  [WARN] {msg}")

    def _print_template_summary(self):
        """Aggregate template-mode roster / placeholder issues at the bottom.

        Errors land under the ``errors`` summary count (so the exit signal
        from ``main`` agrees), warnings under ``warnings``. Both are listed
        per file so the user can act on them directly.
        """
        if not self._template_issues:
            return

        errors = [item for item in self._template_issues if item[0] == 'error']
        warnings = [item for item in self._template_issues if item[0] == 'warning']

        # Mirror into the global summary so downstream "0 errors" gates honor
        # template-mode issues.
        self.summary['errors'] += len(errors)
        self.summary['warnings'] += len(warnings)
        for severity, kind, _msg in self._template_issues:
            self.issue_types[f"template_{kind}"] += 1

        print("\n[TEMPLATE] Template mode checks")
        if errors:
            print(f"  Errors ({len(errors)}):")
            for _sev, kind, msg in errors:
                print(f"    [{kind}] {msg}")
        if warnings:
            print(f"  Warnings ({len(warnings)}):")
            for _sev, kind, msg in warnings:
                print(f"    [{kind}] {msg}")
        if not errors:
            print("  No structural roster issues. Placeholder hints above are advisory only;")
            print("  declare 'placeholders:' frontmatter in design_spec.md to silence them.")

    def _print_drift_summary(self):
        """Print spec_lock drift aggregation if any was observed.

        Values are sorted by file-count descending so frequent drift surfaces
        first. Frequent drift usually means spec_lock.md is missing entries
        the Strategist should have included; rare drift is more likely actual
        Executor drift and warrants SVG review.
        """
        if not self._lock_seen:
            return
        has_drift = any(self._drift_summary[cat] for cat in self._drift_summary)
        if not has_drift:
            print("\n[OK] spec_lock drift: none — all colors, fonts, and sizes are anchored to spec_lock.md")
            return

        print("\nspec_lock drift — values used outside spec_lock.md:")
        labels = [('colors', 'Colors'),
                  ('fonts', 'Font families'),
                  ('sizes', 'Font sizes')]
        for category, label in labels:
            items = self._drift_summary.get(category, {})
            if not items:
                continue
            entries = sorted(items.items(), key=lambda x: (-len(x[1]), x[0]))
            print(f"  {label}:")
            for val, files in entries:
                n = len(files)
                suffix = "file" if n == 1 else "files"
                print(f"    {val}  ({n} {suffix})")
        print(
            "Tip: frequent out-of-lock values usually mean spec_lock.md is missing\n"
            "     entries — extend the lock (scripts/update_spec.py or manual edit).\n"
            "     Rare ones are likely Executor drift — review the affected SVGs."
        )

    def _percentage(self, count: int) -> int:
        """Calculate percentage"""
        if self.summary['total'] == 0:
            return 0
        return int(count / self.summary['total'] * 100)

    def export_report(self, output_file: str = 'svg_quality_report.txt'):
        """Export check report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("PPT Master SVG Quality Check Report\n")
            f.write("=" * 80 + "\n\n")

            for result in self.results:
                status = "[OK] Passed" if result['passed'] else "[ERROR] Failed"
                f.write(f"{status} - {result['file']}\n")
                f.write(f"Path: {result.get('path', 'N/A')}\n")

                if result['info']:
                    f.write(f"Info: {result['info']}\n")

                if result['errors']:
                    f.write(f"\nErrors:\n")
                    for error in result['errors']:
                        f.write(f"  - {error}\n")

                if result['warnings']:
                    f.write(f"\nWarnings:\n")
                    for warning in result['warnings']:
                        f.write(f"  - {warning}\n")

                f.write("\n" + "-" * 80 + "\n\n")

            # Write summary
            f.write("\n" + "=" * 80 + "\n")
            f.write("Check Summary\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total files: {self.summary['total']}\n")
            f.write(f"Fully passed: {self.summary['passed']}\n")
            f.write(f"With warnings: {self.summary['warnings']}\n")
            f.write(f"With errors: {self.summary['errors']}\n")

        print(f"\n[REPORT] Check report exported: {output_file}")


def print_usage() -> None:
    """Print CLI usage information."""
    print("PPT Master - SVG Quality Check Tool\n")
    print("Usage:")
    print("  python3 scripts/svg_quality_checker.py <svg_file>")
    print("  python3 scripts/svg_quality_checker.py <directory>")
    print("  python3 scripts/svg_quality_checker.py <template_dir> --template-mode")
    print("  python3 scripts/svg_quality_checker.py --all examples")
    print("\nExamples:")
    print("  python3 scripts/svg_quality_checker.py examples/project/svg_output/slide_01.svg")
    print("  python3 scripts/svg_quality_checker.py examples/project/svg_output")
    print("  python3 scripts/svg_quality_checker.py examples/project")
    print("  python3 scripts/svg_quality_checker.py templates/layouts/academic_defense --template-mode")
    print("  python3 scripts/svg_quality_checker.py templates/decks/招商银行 --template-mode")
    print("\nOptions:")
    print("  --format <ppt169|ppt43|...>   Expected canvas format")
    print("  --template-mode               Validate a templates/{layouts,decks}/<id> directory:")
    print("                                  glob *.svg directly, skip spec_lock checks,")
    print("                                  enforce roster ↔ design_spec.md Page Roster consistency,")
    print("                                  and emit advisory placeholder-convention warnings.")


def _svgqc_content_hash(files: List[Path]) -> str:
    """sha256 over the sorted SVG file contents.

    health-fork: MUST stay byte-for-byte identical to
    svg_to_pptx.pptx_cli.svgqc_content_hash, or the export gate would see a
    false mismatch on every run. Keep the two in sync.
    """
    h = hashlib.sha256()
    for path in sorted(files, key=lambda p: p.name):
        h.update(path.name.encode('utf-8'))
        h.update(b'\0')
        try:
            h.update(path.read_bytes())
        except OSError:
            h.update(b'<unreadable>')
        h.update(b'\0')
    return h.hexdigest()


def _write_svgqc_sentinel(target: str, summary: Dict) -> None:
    """health-fork: on a clean (0-error) project check, drop <project>/.svgqc_pass.json.

    The export gate (pptx_cli) refuses/warns unless this sentinel exists and its
    content_hash matches the svg_output/ SVGs about to be exported. Only written
    for a project/svg_output target with 0 errors — never for single files,
    --all, or --template-mode.
    """
    if summary.get('errors', 0) != 0:
        return
    tpath = Path(target)
    if tpath.is_file():
        return  # single-file check — no project sentinel
    if not tpath.is_dir():
        return
    # Resolve (project_dir, svg_dir) exactly as check_directory / pptx_cli do.
    if (tpath / 'svg_output').is_dir():
        project_dir, svg_dir = tpath, tpath / 'svg_output'
    elif tpath.name == 'svg_output':
        project_dir, svg_dir = tpath.parent, tpath
    else:
        project_dir, svg_dir = tpath, tpath
    svg_files = sorted(svg_dir.glob('*.svg'))
    if not svg_files:
        return
    sentinel = {
        'svg_dir': svg_dir.name,
        'content_hash': _svgqc_content_hash(svg_files),
        'file_count': len(svg_files),
        'errors': 0,
        'warnings': summary.get('warnings', 0),
        'ts': datetime.now().isoformat(timespec='seconds'),
    }
    try:
        (project_dir / '.svgqc_pass.json').write_text(
            json.dumps(sentinel, ensure_ascii=False, indent=2), encoding='utf-8'
        )
    except OSError:
        pass  # sentinel is best-effort; never fail the check on a write error


def main() -> None:
    """Run the CLI entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    if sys.argv[1] in {"-h", "--help", "help"}:
        print_usage()
        sys.exit(0)

    if sys.argv[1].startswith("--") and sys.argv[1] not in {"--all"}:
        print(f"[ERROR] Missing target before option: {sys.argv[1]}")
        print_usage()
        sys.exit(1)

    template_mode = '--template-mode' in sys.argv
    checker = SVGQualityChecker(template_mode=template_mode)

    # Parse arguments
    target = sys.argv[1]
    expected_format = None

    if '--format' in sys.argv:
        idx = sys.argv.index('--format')
        if idx + 1 < len(sys.argv):
            expected_format = sys.argv[idx + 1]

    # Execute check
    if target == '--all':
        # Check all example projects
        base_dir = sys.argv[2] if len(sys.argv) > 2 else 'examples'
        from project_utils import find_all_projects
        projects = find_all_projects(base_dir)

        for project in projects:
            print(f"\n{'=' * 80}")
            print(f"Checking project: {project.name}")
            print('=' * 80)
            checker.check_directory(str(project))
    else:
        checker.check_directory(target, expected_format)

    # Print summary
    checker.print_summary()

    # health-fork: emit the quality sentinel for the export gate (clean project
    # checks only; skipped for --all and --template-mode).
    if target != '--all' and not template_mode:
        _write_svgqc_sentinel(target, checker.summary)

    # Export report (if specified)
    if '--export' in sys.argv:
        output_file = 'svg_quality_report.txt'
        if '--output' in sys.argv:
            idx = sys.argv.index('--output')
            if idx + 1 < len(sys.argv):
                output_file = sys.argv[idx + 1]
        checker.export_report(output_file)

    # Return exit code
    if checker.summary['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
