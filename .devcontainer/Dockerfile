FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends inkscape ghostscript imagemagick make zip xvfb x11vnc fluxbox novnc websockify \
    && rm -rf /var/lib/apt/lists/*
