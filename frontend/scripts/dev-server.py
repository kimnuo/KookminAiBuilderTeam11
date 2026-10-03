from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "build" / "web"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if not (WEB / "index.html").exists():
    raise SystemExit("Run flutter build web before opening the preview.")
ThreadingHTTPServer(("127.0.0.1", 4173), Handler).serve_forever()
