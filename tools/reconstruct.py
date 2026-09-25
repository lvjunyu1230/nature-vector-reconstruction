#!/usr/bin/env python3
"""Turn a flat raster reference into an editable, sanitized SVG.

The reference image is treated as a visual guide. VTracer performs the first
geometric conversion; the sanitizer removes raster and effect constructs so
that the deliverable is path/shape based and can be edited in Inkscape.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lxml import etree
from PIL import Image
import yaml

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

FORBIDDEN_TAGS = {
    "image", "filter", "linearGradient", "radialGradient", "pattern", "mask",
    "clipPath", "style", "metadata", "namedview", "foreignObject", "script", "defs",
}
SHAPE_TAGS = {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line"}
TRACE_KEYS = {
    "colormode", "hierarchical", "mode", "filter_speckle", "color_precision",
    "layer_difference", "corner_threshold", "length_threshold", "max_iterations",
    "splice_threshold", "path_precision",
}


def q(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def local_name(tag: Any) -> str:
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def hex_rgb(value: str) -> tuple[int, int, int] | None:
    value = str(value).strip()
    if value.startswith("#"):
        raw = value[1:]
        if len(raw) == 3:
            raw = "".join(ch * 2 for ch in raw)
        if len(raw) == 6:
            try:
                return tuple(int(raw[i:i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                return None
    if value.lower().startswith("rgb(") and value.endswith(")"):
        try:
            nums = [int(float(x.strip())) for x in value[4:-1].split(",")[:3]]
            if len(nums) == 3:
                return tuple(max(0, min(255, n)) for n in nums)
        except ValueError:
            return None
    return None


def rgb_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % rgb


def nearest_color(value: str, palette: list[str]) -> str:
    rgb = hex_rgb(value)
    if rgb is None or not palette:
        return value
    candidates = [(p, hex_rgb(p)) for p in palette]
    candidates = [(p, c) for p, c in candidates if c is not None]
    if not candidates:
        return value
    # Perceptual enough for a compact flat palette; keeps this tool dependency-light.
    def distance(item: tuple[str, tuple[int, int, int]]) -> float:
        _, c = item
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, c)))
    return min(candidates, key=distance)[0]


def read_style(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data


def parse_inline_style(style: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in style.split(";"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def flatten_and_prepare(input_path: Path, work_dir: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    input_cfg = cfg.get("input", {})
    paper = str(cfg.get("output", {}).get("paper", "#FFFEFC"))
    paper_rgb = hex_rgb(paper) or (255, 254, 252)
    image = Image.open(input_path).convert("RGBA")
    original_size = image.size

    # Transparent references are composited on the final paper color before tracing.
    background = Image.new("RGBA", image.size, (*paper_rgb, 255))
    background.alpha_composite(image)
    rgb = background.convert("RGB")

    max_dimension = int(input_cfg.get("max_dimension", 2400))
    if max_dimension > 0 and max(rgb.size) > max_dimension:
        scale = max_dimension / max(rgb.size)
        size = (max(1, round(rgb.width * scale)), max(1, round(rgb.height * scale)))
        rgb = rgb.resize(size, Image.Resampling.LANCZOS)

    colors = int(input_cfg.get("quantize_colors", 24))
    if colors > 0:
        rgb = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")

    prepared = work_dir / "prepared.png"
    rgb.save(prepared, format="PNG", optimize=True)
    return {
        "prepared": prepared,
        "original_size": original_size,
        "prepared_size": rgb.size,
        "input_mode": image.mode,
        "input_sha256": sha256(input_path),
    }


def trace_image(prepared: Path, raw_svg: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    try:
        import vtracer  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "vtracer is not installed. Run `python3 -m pip install -r requirements.txt`."
        ) from exc

    trace_cfg = cfg.get("trace", {})
    kwargs = {key: trace_cfg[key] for key in TRACE_KEYS if key in trace_cfg}
    vtracer.convert_image_to_svg_py(str(prepared), str(raw_svg), **kwargs)
    version = getattr(vtracer, "__version__", "unknown")
    return {"engine": "VTracer", "version": version, "parameters": kwargs}


def sanitize_svg(raw_svg: Path, output_svg: Path, prepared_size: tuple[int, int], cfg: dict[str, Any]) -> dict[str, Any]:
    parser = etree.XMLParser(remove_comments=True, resolve_entities=False, no_network=True)
    tree = etree.parse(str(raw_svg), parser)
    root = tree.getroot()
    output_cfg = cfg.get("output", {})
    paper = str(output_cfg.get("paper", "#FFFEFC"))
    palette_mode = str(output_cfg.get("palette_mode", "nearest"))
    palette = [str(x) for x in output_cfg.get("palette", [])]

    # Move only geometric content into a named layer; remove effects, source metadata,
    # and all external references before writing the final file.
    geometric = etree.Element(q("g"), id="vectorized-reference")
    removed = 0

    def prune(element: etree._Element) -> None:
        nonlocal removed
        for child in list(element):
            tag = local_name(child.tag)
            href = child.get("href") or child.get(f"{{{XLINK_NS}}}href")
            if tag in FORBIDDEN_TAGS or href:
                element.remove(child)
                removed += 1
                continue
            prune(child)

    for child in list(root):
        root.remove(child)
        tag = local_name(child.tag)
        if tag in FORBIDDEN_TAGS:
            removed += 1
            continue
        href = child.get("href") or child.get(f"{{{XLINK_NS}}}href")
        if href:
            removed += 1
            continue
        prune(child)
        geometric.append(child)

    for element in geometric.iter():
        if local_name(element.tag) not in SHAPE_TAGS:
            continue
        inline = parse_inline_style(element.get("style", ""))
        if "fill" not in element.attrib and "fill" in inline:
            element.set("fill", inline["fill"])
        if "stroke" not in element.attrib and "stroke" in inline:
            element.set("stroke", inline["stroke"])
        element.attrib.pop("style", None)
        if palette_mode == "nearest" and palette:
            fill = element.get("fill")
            if fill and fill.lower() != "none":
                element.set("fill", nearest_color(fill, palette))
            stroke = element.get("stroke")
            if stroke and stroke.lower() != "none":
                element.set("stroke", nearest_color(stroke, palette))

    width, height = prepared_size
    root.set("version", "1.1")
    page_width_mm = output_cfg.get("page_width_mm")
    if page_width_mm:
        physical_width = float(page_width_mm)
        physical_height = physical_width * height / width
        root.set("width", f"{physical_width:g}mm")
        root.set("height", f"{physical_height:.3f}mm")
    else:
        root.set("width", str(width))
        root.set("height", str(height))
    root.set("viewBox", f"0 0 {width} {height}")
    if output_cfg.get("add_background", True):
        root.append(etree.Element(q("rect"), {
            "id": "paper",
            "x": "0", "y": "0", "width": str(width), "height": str(height),
            "fill": paper,
        }))
    root.append(geometric)

    output_svg.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_svg), encoding="UTF-8", xml_declaration=True, pretty_print=True)
    all_tags = [local_name(el.tag) for el in etree.parse(str(output_svg)).getroot().iter()]
    return {
        "removed_elements": removed,
        "paths": all_tags.count("path"),
        "shapes": sum(all_tags.count(tag) for tag in ("path", "rect", "circle", "ellipse", "polygon", "polyline", "line")),
        "forbidden_remaining": sorted(set(all_tags) & FORBIDDEN_TAGS),
    }


def write_report(path: Path, input_path: Path, output_path: Path, prep: dict[str, Any], engine: dict[str, Any], clean: dict[str, Any], cfg: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    trace_params = engine.get("parameters", {})
    lines = [
        "# Reconstruction report",
        "",
        "This file records the deterministic raster-to-vector run. The reference image is not embedded in the SVG.",
        "",
        "## Inputs",
        "",
        f"- Reference: `{input_path.name}`",
        f"- SHA-256: `{prep['input_sha256']}`",
        f"- Original pixels: `{prep['original_size'][0]} × {prep['original_size'][1]}`",
        f"- Traced pixels: `{prep['prepared_size'][0]} × {prep['prepared_size'][1]}`",
        f"- Input mode: `{prep['input_mode']}`",
        "",
        "## Engine",
        "",
        f"- `{engine.get('engine')}` `{engine.get('version')}`",
        f"- Parameters: `{trace_params}`",
        f"- Generated (UTC): `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Output checks",
        "",
        f"- SVG: `{output_path}`",
        f"- SHA-256: `{sha256(output_path)}`",
        f"- Editable path count: `{clean['paths']}`",
        f"- Geometric shape count: `{clean['shapes']}`",
        f"- Removed forbidden/source elements: `{clean['removed_elements']}`",
        f"- Forbidden elements remaining: `{clean['forbidden_remaining']}`",
        "",
        "## Interpretation",
        "",
        "The SVG is path/shape based and contains no embedded raster. Automatic tracing preserves the visual content of the reference; journal-ready semantic cleanup (labels, arrows, axes, repeated objects and scientific meaning) should be reviewed in Inkscape.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="PNG/JPG/WebP reference image")
    parser.add_argument("--output", required=True, type=Path, help="destination SVG")
    parser.add_argument("--style", type=Path, default=Path("config/style.yaml"))
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--keep-intermediate", action="store_true", help="keep prepared PNG next to output")
    parser.add_argument("--palette-mode", choices=("nearest", "keep"), default=None)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2
    cfg = read_style(args.style)
    if args.palette_mode:
        cfg.setdefault("output", {})["palette_mode"] = args.palette_mode

    temp_root: Path | None = None
    try:
        if args.keep_intermediate:
            temp_root = args.output.parent / ".intermediate"
            temp_root.mkdir(parents=True, exist_ok=True)
            work_dir = temp_root
        else:
            temp_root = Path(tempfile.mkdtemp(prefix="vector-reconstruct-"))
            work_dir = temp_root
        prep = flatten_and_prepare(args.input, work_dir, cfg)
        engine = trace_image(prep["prepared"], work_dir / "raw.svg", cfg)
        clean = sanitize_svg(work_dir / "raw.svg", args.output, prep["prepared_size"], cfg)
        report = args.report or args.output.with_name(args.output.stem + "_report.md")
        write_report(report, args.input, args.output, prep, engine, clean, cfg)
        print(f"SVG written: {args.output}")
        print(f"Report written: {report}")
        print(f"Paths: {clean['paths']}; geometric shapes: {clean['shapes']}")
        return 0
    except Exception as exc:  # CLI should expose a useful actionable error.
        print(f"Reconstruction failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if temp_root and not args.keep_intermediate:
            shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
