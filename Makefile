PYTHON ?= python3
INPUT ?= $(firstword $(wildcard input/*.png input/*.jpg input/*.jpeg input/*.webp))
OUTDIR ?= outputs
SVG ?= $(OUTDIR)/reconstructed.svg
REPORT ?= $(OUTDIR)/reconstruction_report.md

.PHONY: setup reconstruct qa export all clean

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

all: export

clean:
	find $(OUTDIR) -type f ! -name .gitkeep -delete
