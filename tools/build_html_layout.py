#!/usr/bin/env python3
"""Build a responsive HTML page from standalone inline-SVG modules.

The HTML page is a layout and review surface. The scientific marks remain SVG
paths/text, so the same modules can later be exported or refined in a vector
editor. The manifest is deliberately small and human-editable.
"""
from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from lxml import etree


DEFAULT_CSS = """
:root {
  --page-max-width: 1190px;
  --page-padding: clamp(14px, 2vw, 28px);
  --module-gap: clamp(12px, 2vw, 30px);
}
* { box-sizing: border-box; }
html, body { margin: 0; background: #fff; color: #27323b; }
body { font-family: Arial, Helvetica, sans-serif; }
.figure-page { width: min(100%, var(--page-max-width)); margin: 0 auto; padding: var(--page-padding); }
.figure-title { margin: 0 0 14px; font-size: 18px; font-weight: 600; }
.comparison { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: clamp(24px, 4vw, 64px); align-items: start; }
.comparison h2 { margin: 0 0 10px; font-size: 13px; font-weight: 600; color: #59636b; }
.fixed-preview { width: 100%; height: auto; display: block; }
.module-grid { display: grid; grid-template-columns: var(--module-columns, 1.7fr 1.42fr .78fr .94fr); gap: var(--module-gap); align-items: start; }
.module { min-width: 0; }
.module-svg { width: 100%; height: auto; display: block; overflow: visible; }
.figure-note { margin: 12px 0 0; color: #66717a; font-size: 12px; line-height: 1.45; }
@media (max-width: 1050px) {
  .comparison { grid-template-columns: 1fr; }
}
@media (max-width: 720px) {
  .module-grid { grid-template-columns: 1fr 1fr; row-gap: 24px; }
}
@media print {
  .figure-page { width: 100%; padding: 0; }
  .comparison { display: block; }
  .fixed-block { display: none; }
  .module-grid { grid-template-columns: var(--module-columns, 1.7fr 1.42fr .78fr .94fr); gap: 16px; }
}
"""


def read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


SVG_NS = "http://www.w3.org/2000/svg"


def q(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def parse_viewbox(root: etree._Element) -> tuple[float, float, float, float]:
    raw = root.get("viewBox") or root.get("viewbox")
    if not raw:
        raise ValueError("each module SVG must define a viewBox")
    values = [float(x) for x in raw.replace(",", " ").split()]
    if len(values) != 4:
        raise ValueError(f"invalid viewBox: {raw}")
    return tuple(values)  # type: ignore[return-value]


def write_static_svg(manifest: dict, manifest_path: Path, output_path: Path) -> None:
    canvas = manifest.get("canvas", {"width": 1190, "height": 410})
    width = float(canvas.get("width", 1190))
    height = float(canvas.get("height", 410))
    nsmap = {None: SVG_NS}
    svg = etree.Element(q("svg"), nsmap=nsmap, width=str(width), height=str(height), viewBox=f"0 0 {width:g} {height:g}")
    etree.SubElement(svg, q("title")).text = str(manifest.get("title", "HTML + inline SVG layout"))
    etree.SubElement(svg, q("rect"), x="0", y="0", width=str(width), height=str(height), fill="#ffffff")

    first_defs: etree._Element | None = None
    module_nodes: list[tuple[dict, etree._Element, tuple[float, float, float, float]]] = []
    base = manifest_path.parent
    for module in manifest.get("modules", []):
        path = (base / module["svg"]).resolve()
        module_root = etree.parse(str(path)).getroot()
        if first_defs is None:
            defs = module_root.find(q("defs"))
            if defs is not None:
                first_defs = etree.fromstring(etree.tostring(defs))
        module_nodes.append((module, module_root, parse_viewbox(module_root)))
    if first_defs is not None:
        svg.insert(1, first_defs)

    for module, module_root, (vx, vy, _vw, _vh) in module_nodes:
        placement = module.get("placement", {})
        x = float(placement.get("x", 0))
        y = float(placement.get("y", 0))
        scale = float(placement.get("scale", 1))
        group = etree.SubElement(svg, q("g"), id=f"module-{module.get('id', 'unnamed')}", transform=f"translate({x:g} {y:g}) scale({scale:g}) translate({-vx:g} {-vy:g})")
        for child in module_root:
            if child.tag in {q("defs"), q("title"), q("desc")}:
                continue
            group.append(etree.fromstring(etree.tostring(child)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    etree.ElementTree(svg).write(str(output_path), encoding="UTF-8", xml_declaration=True, pretty_print=True)


def build(manifest_path: Path, output_path: Path, static_svg_path: Path | None = None) -> None:
    manifest = read_manifest(manifest_path)
    base = manifest_path.parent
    fixed_svg = manifest.get("fixed_svg")
    fixed_markup = ""
    if fixed_svg:
        fixed_path = (base / fixed_svg).resolve()
        fixed_svg_markup = fixed_path.read_text(encoding="utf-8")
        if "<?xml" in fixed_svg_markup:
            fixed_svg_markup = fixed_svg_markup[fixed_svg_markup.find("?>") + 2 :]
        fixed_markup = f'''<section class="fixed-block">
  <h2>Reference / fixed-coordinate SVG</h2>
  <div class="fixed-preview" role="img" aria-label="Fixed-coordinate SVG preview">
{fixed_svg_markup.strip()}
  </div>
  <p class="figure-note">The original vector composition is retained as a fixed-coordinate reference.</p>
</section>'''

    columns = str(manifest.get("columns", "1.7fr 1.42fr .78fr .94fr"))
    modules = []
    for module in manifest.get("modules", []):
        module_path = (base / module["svg"]).resolve()
        svg = module_path.read_text(encoding="utf-8")
        # Keep only the SVG document itself; XML declarations are invalid inside HTML.
        if "<?xml" in svg:
            svg = svg[svg.find("?>") + 2 :]
        modules.append(f'''<section class="module" aria-label="{escape(str(module.get('title', module['id'])))}">
{svg.strip()}
</section>''')

    title = escape(str(manifest.get("title", "HTML + inline SVG scientific figure")))
    note = escape(str(manifest.get("note", "HTML/CSS controls layout; inline SVG preserves editable scientific objects.")))
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
{DEFAULT_CSS}
  </style>
</head>
<body>
  <main class="figure-page">
    <h1 class="figure-title">{title}</h1>
    <div class="comparison">
      {fixed_markup}
      <section>
        <h2>HTML + inline SVG layout</h2>
        <div class="module-grid" style="--module-columns: {escape(columns)};">
          {''.join(modules)}
        </div>
        <p class="figure-note">{note}</p>
      </section>
    </div>
  </main>
</body>
</html>
'''
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    if static_svg_path is not None:
        write_static_svg(manifest, manifest_path, static_svg_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--static-svg", type=Path, default=None, help="also write a fixed SVG composition using manifest placements")
    args = parser.parse_args()
    if not args.manifest.exists():
        parser.error(f"manifest not found: {args.manifest}")
    build(args.manifest, args.output, args.static_svg)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
