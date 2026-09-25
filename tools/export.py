#!/usr/bin/env python3
"""Export a clean SVG to PDF, EPS and PNG with the Inkscape CLI."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("svg", type=Path)
    parser.add_argument("--outdir", type=Path, default=Path("outputs"))
    parser.add_argument("--png-width", type=int, default=2400)
    args = parser.parse_args()
    inkscape = shutil.which("inkscape")
    if not inkscape:
        print("Inkscape was not found. Open a Codespace or run the GitHub Actions workflow; no local installation is required.", file=sys.stderr)
        return 2
    if not args.svg.exists():
        print(f"SVG not found: {args.svg}", file=sys.stderr)
        return 2
    args.outdir.mkdir(parents=True, exist_ok=True)
    stem = args.svg.stem
    for suffix in ("pdf", "eps"):
        output = args.outdir / f"{stem}.{suffix}"
        subprocess.run([inkscape, str(args.svg), f"--export-filename={output}"], check=True)
        print(f"Wrote {output}")
    png = args.outdir / f"{stem}.png"
    subprocess.run([inkscape, str(args.svg), f"--export-filename={png}", f"--export-width={args.png_width}"], check=True)
    print(f"Wrote {png}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
