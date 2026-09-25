#!/usr/bin/env bash
set -euo pipefail
pkill -x inkscape || true
pkill -x fluxbox || true
pkill -f 'x11vnc.*5900' || true
pkill -f 'Xvfb :1' || true
pkill -f 'websockify.*6080' || true
