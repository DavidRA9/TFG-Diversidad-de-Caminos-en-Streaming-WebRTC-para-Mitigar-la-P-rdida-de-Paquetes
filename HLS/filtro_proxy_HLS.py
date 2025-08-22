#!/usr/bin/env python3

from mitmproxy import ctx
import os
import datetime

class filtro_proxy:
    def __init__(self):
        ctx.log.warn("filtro_proxy class initiated")
        self.segment_files = []
        self.output_dir = os.path.join("grabaciones", datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        os.makedirs(self.output_dir, exist_ok=True)

    def writefile(self, filename, content):
        ctx.log.warn(f"Writing File: {filename}")
        path = os.path.join(self.output_dir, filename)
        with open(path, "wb") as f:
            f.write(content)

    def log_segment_timestamp(self, segment_name, event_type):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        filename = f"segment_{event_type}_log.txt"
        path = os.path.join(self.output_dir, filename)
        with open(path, "a") as log:
            log.write(f"{now} - {segment_name}\n")

    def request(self, flow):
        url = flow.request.path
        filename = os.path.basename(url)

        if url.endswith(".ts"):
            self.log_segment_timestamp(filename, "request")

    def response(self, flow):
        url = flow.request.path
        filename = os.path.basename(url)

        # Guardar segmentos .ts (HLS)
        if url.endswith(".ts"):
            self.writefile(filename, flow.response.content)
            self.segment_files.append(filename)
            self.log_segment_timestamp(filename, "latency")

        # Guardar playlist .m3u8
        elif url.endswith(".m3u8"):
            self.writefile(filename, flow.response.content)
            ctx.log.warn(f"Guardado manifest: {filename}")

addons = [filtro_proxy()]



