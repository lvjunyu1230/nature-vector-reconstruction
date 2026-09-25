FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip inkscape ghostscript imagemagick make zip \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt
COPY . /work
CMD ["make", "all"]
