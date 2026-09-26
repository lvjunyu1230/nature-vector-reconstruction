PYTHON ?= python3
INPUT ?= $(firstword $(wildcard input/*.png input/*.jpg input/*.jpeg input/*.webp))
OUTDIR ?= outputs
SVG ?= $(OUTDIR)/reconstructed.svg
REPORT ?= $(OUTDIR)/reconstruction_report.md
HTML_MANIFEST ?= examples/panel_c_html_layout/layout.json
HTML_OUTPUT ?= $(OUTDIR)/panel_c_html_layout.html
HTML_SVG ?= $(OUTDIR)/panel_c_html_layout.svg

.PHONY: setup reconstruct qa export legacy-all html all clean

setup:
	$(PYTHON) -m pip install -r requirements.txt

reconstruct:
	@test -n "$(INPUT)" || (echo "Put one PNG/JPG/WebP reference image in input/" && exit 2)
	mkdir -p $(OUTDIR)
	$(PYTHON) tools/reconstruct.py --input "$(INPUT)" --output "$(SVG)" --style config/style.yaml --report "$(REPORT)"

qa: reconstruct
	$(PYTHON) tools/qa.py "$(SVG)" --report $(OUTDIR)/qa_report.md

export: qa
	$(PYTHON) tools/export.py "$(SVG)" --outdir $(OUTDIR)

# The default route now builds the HTML + inline-SVG layout surface.
# The previous raster-trace/Inkscape route remains available as legacy-all.
html:
	mkdir -p $(OUTDIR)
	$(PYTHON) tools/build_html_layout.py --manifest "$(HTML_MANIFEST)" --output "$(HTML_OUTPUT)" --static-svg "$(HTML_SVG)"
	$(PYTHON) tools/qa.py "$(HTML_SVG)" --report "$(OUTDIR)/html_layout_qa_report.md"

all: html

legacy-all: export

clean:
	find $(OUTDIR) -type f ! -name .gitkeep -delete
