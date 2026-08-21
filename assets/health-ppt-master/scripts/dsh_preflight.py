#!/usr/bin/env python3
"""Report local capabilities used by health-ppt-master without exposing secrets."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA = "health-ppt-master-preflight.v1"
CORE_REQUIREMENTS = Path(__file__).resolve().parent.parent / "requirements-core.txt"
MODULE_GROUPS = {
    "core": (
        ("python-pptx", "pptx"),
        ("Pillow", "PIL"),
        ("svglib", "svglib"),
        ("reportlab", "reportlab"),
        ("PyYAML", "yaml"),
    ),
    "ingestion": (
        ("PyMuPDF", "fitz"),
        ("mammoth", "mammoth"),
        ("markdownify", "markdownify"),
        ("EbookLib", "ebooklib"),
        ("nbconvert", "nbconvert"),
        ("openpyxl", "openpyxl"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("curl_cffi", "curl_cffi"),
    ),
    "preview": (
        ("Flask", "flask"),
        ("playwright", "playwright"),
    ),
    "audio": (("edge-tts", "edge_tts"),),
}
PROGRAM_GROUPS = {
    "audio": (("ffmpeg",), ("ffprobe",)),
    "office": (("libreoffice", "soffice"),),
}
GROUPS = ("core", "ingestion", "preview", "audio", "office", "document-parser", "workspace")


def module_check(distribution: str, module: str) -> dict[str, Any]:
    """Return availability and installed distribution version for one import."""
    try:
        available = importlib.util.find_spec(module) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        available = False
    version = None
    if available:
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            pass
    return {
        "kind": "python-module",
        "name": distribution,
        "import": module,
        "available": available,
        "version": version,
    }


def program_check(alternatives: tuple[str, ...]) -> dict[str, Any]:
    """Return the first executable found for one alternative set."""
    resolved = None
    for name in alternatives:
        candidate = shutil.which(name)
        if candidate is not None:
            resolved = candidate
            break
    return {
        "kind": "program",
        "name": alternatives[0],
        "alternatives": list(alternatives),
        "available": resolved is not None,
        "path": resolved,
    }


def chromium_check() -> dict[str, Any]:
    """Check whether Playwright knows an installed Chromium executable."""
    code = (
        "from pathlib import Path\n"
        "from playwright.sync_api import sync_playwright\n"
        "with sync_playwright() as p:\n"
        " print(p.chromium.executable_path)\n"
        " raise SystemExit(0 if Path(p.chromium.executable_path).is_file() else 2)\n"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {
            "kind": "program",
            "name": "playwright-chromium",
            "alternatives": [],
            "available": False,
            "path": None,
        }
    path = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else None
    return {
        "kind": "program",
        "name": "playwright-chromium",
        "alternatives": [],
        "available": result.returncode == 0,
        "path": path,
    }


def path_check(name: str, path: Path | None, expected: Path | None = None) -> dict[str, Any]:
    """Validate a caller-supplied workspace or deployment resource path."""
    resolved = path.expanduser().resolve() if path is not None else None
    target = resolved / expected if resolved is not None and expected is not None else resolved
    available = target is not None and target.exists()
    if available and name == "workspace":
        available = target.is_dir() and os.access(target, os.W_OK | os.X_OK)
    return {
        "kind": "path",
        "name": name,
        "available": available,
        "configured": path is not None,
        "path": str(resolved) if resolved is not None else None,
        "expected": str(expected) if expected is not None else None,
    }


def collect(workspace: Path | None, document_parser_dir: Path | None) -> dict[str, list[dict[str, Any]]]:
    """Collect all capability groups without reading credential values."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for group, modules in MODULE_GROUPS.items():
        groups[group] = [module_check(distribution, module) for distribution, module in modules]
    for group, programs in PROGRAM_GROUPS.items():
        groups.setdefault(group, []).extend(program_check(names) for names in programs)
    if groups["preview"][1]["available"]:
        groups["preview"].append(chromium_check())
    else:
        groups["preview"].append({
            "kind": "program",
            "name": "playwright-chromium",
            "alternatives": [],
            "available": False,
            "path": None,
        })
    groups["document-parser"] = [path_check(
        "document-parser",
        document_parser_dir,
        Path("scripts/pdf_dispatcher.py"),
    )]
    groups["workspace"] = [path_check("workspace", workspace)]
    return groups


def render_plain(report: dict[str, Any]) -> None:
    """Print a compact human-readable report."""
    print(f"health-ppt-master preflight: {'PASS' if report['ok'] else 'BLOCKED'}")
    for group, value in report["groups"].items():
        required = " required" if group in report["required"] else ""
        print(f"- {group}: {'ready' if value['ok'] else 'missing'}{required}")
        for check in value["checks"]:
            if check["available"]:
                detail = check.get("version") or check.get("path") or "available"
            elif check.get("configured") is False:
                detail = "not configured"
            else:
                detail = "not found"
            print(f"  - {check['name']}: {detail}")
    if "core" in report["required"] and not report["groups"]["core"]["ok"]:
        print(f"Install core packages in a workspace virtual environment from: {CORE_REQUIREMENTS}")


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, emit a report, and fail only for explicitly required groups."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require", action="append", choices=GROUPS, default=[])
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--document-parser-dir", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    checks = collect(args.workspace, args.document_parser_dir)
    groups = {
        group: {"ok": all(check["available"] for check in values), "checks": values}
        for group, values in checks.items()
    }
    ok = all(groups[group]["ok"] for group in args.require)
    report = {
        "schema": SCHEMA,
        "python": {"executable": sys.executable, "version": sys.version.split()[0]},
        "required": args.require,
        "ok": ok,
        "resources": {"coreRequirements": str(CORE_REQUIREMENTS)},
        "groups": groups,
    }
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        render_plain(report)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
