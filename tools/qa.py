#!/usr/bin/env python3
"""Fail fast when a deliverable SVG still contains raster/effect constructs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from lxml import etree

FORBIDDEN = {"image", "filter", "linearGradient", "radialGradient", "pattern", "mask", "foreignObject", "script"}
SVG_NS = "http://www.w3.org/2000/svg"

def local_name(tag: object) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("svg", type=Path)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    if not args.svg.exists():
        print(f"SVG not found: {args.svg}", file=sys.stderr)
        return 2
    try:
        root = etree.parse(str(args.svg), etree.XMLParser(resolve_entities=False, no_network=True)).getroot()
    except Exception as exc:
        print(f"XML parse failed: {exc}", file=sys.stderr)
        return 1

    tags = [local_name(el.tag) for el in root.iter()]
    forbidden = sorted(set(tags) & FORBIDDEN)
    external_refs = []
    for el in root.iter():
        for key, value in el.attrib.items():
            if key.endswith("href") and value:
                external_refs.append({"tag": local_name(el.tag), "attribute": key, "value": value})
    shapes = sum(tags.count(tag) for tag in ("path", "rect", "circle", "ellipse", "polygon", "polyline", "line"))
    result = {
        "svg": str(args.svg),
        "viewBox": root.get("viewBox"),
        "paths": tags.count("path"),
        "shapes": shapes,
        "forbidden_tags": forbidden,
        "external_references": external_refs,
        "pass": not forbidden and not external_refs and shapes > 0 and bool(root.get("viewBox")),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            "# SVG QA report\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```\n",
            encoding="utf-8",
        )
    if not result["pass"]:
        print("SVG QA failed: remove raster/effect elements or add a viewBox.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
