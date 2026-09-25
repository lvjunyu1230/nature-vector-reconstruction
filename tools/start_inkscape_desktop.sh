#!/usr/bin/env bash
set -euo pipefail

DISPLAY=:1
SCREEN_SIZE="${INKSCAPE_SCREEN_SIZE:-1600x1000x24}"

if ! pgrep -f "Xvfb ${DISPLAY}" >/dev/null 2>&1; then
  Xvfb "${DISPLAY}" -screen 0 "${SCREEN_SIZE}" -nolisten tcp -ac >/tmp/inkscape-xvfb.log 2>&1 &
fi
export DISPLAY
sleep 1

if ! pgrep -x fluxbox >/dev/null 2>&1; then
  fluxbox >/tmp/inkscape-fluxbox.log 2>&1 &
fi
if ! pgrep -f "x11vnc.*5900" >/dev/null 2>&1; then
  x11vnc -display "${DISPLAY}" -rfbport 5900 -forever -shared -localhost -nopw >/tmp/inkscape-x11vnc.log 2>&1 &
fi
sleep 1

if [ "$#" -gt 0 ]; then
  inkscape "$@" >/tmp/inkscape-gui.log 2>&1 &
else
  inkscape >/tmp/inkscape-gui.log 2>&1 &
fi

# Codespaces forwards this private port; VNC itself only listens on localhost.
exec websockify --web=/usr/share/novnc/ 6080 127.0.0.1:5900
