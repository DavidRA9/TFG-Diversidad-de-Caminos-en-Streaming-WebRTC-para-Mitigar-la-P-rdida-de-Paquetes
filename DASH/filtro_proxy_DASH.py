#!/usr/bin/env python3

from mitmproxy import ctx
import os
import datetime

class filtro_proxy:
    def __init__(self):
        ctx.log.warn("filtro_proxy class initiated")
        self.segment_files = []
        self.init_file = None

        # Carpeta base + timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dir = os.path.join("grabaciones", timestamp)
        os.makedirs(self.output_dir, exist_ok=True)

    def writefile(self, filename, content):
        ctx.log.warn(f"Writing File: {filename}")
        path = os.path.join(self.output_dir, filename)
        with open(path, "wb") as f:
            f.write(content)

    def write_filelist(self):
        path = os.path.join(self.output_dir, "filelist.txt")
        with open(path, "w") as filelist:
            if self.init_file:
                filelist.write(f"file '{self.init_file}'\n")
            for segment in self.segment_files:
                filelist.write(f"file '{segment}'\n")

    def log_segment_timestamp(self, segment_name):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        path = os.path.join(self.output_dir, "segment_latency_log.txt")
        with open(path, "a") as log:
            log.write(f"{now} - {segment_name}\n")

    def log_segment_request(self, segment_name):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        path = os.path.join(self.output_dir, "segment_request_log.txt")
        with open(path, "a") as log:
            log.write(f"{now} - {segment_name}\n")

    def request(self, flow):
        url = flow.request.path
        if url.endswith(".m4s"):
            filename = os.path.basename(url)
            self.log_segment_request(filename)

    def response(self, flow):
        url = flow.request.path

        if url.endswith(".m4s"):
            filename = os.path.basename(url)
            self.writefile(filename, flow.response.content)
            self.segment_files.append(filename)
            self.write_filelist()
            self.log_segment_timestamp(filename)

        elif "init" in url and (".mp4" in url or ".m4s" in url):
            filename = "init_" + os.path.basename(url)
            self.writefile(filename, flow.response.content)
            if not self.init_file:
                self.init_file = filename
            self.write_filelist()

addons = [filtro_proxy()]


