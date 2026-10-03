from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

FRONTEND = Path(__file__).resolve().parents[1]
MOCK = FRONTEND.parent / "mock"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def translate_path(self, path):
        route = unquote(urlsplit(path).path)
        if route.startswith("/mock/"):
            target = (MOCK / route.removeprefix("/mock/")).resolve()
            return str(target if target.is_relative_to(MOCK) else MOCK / "missing")
        return super().translate_path(path)


ThreadingHTTPServer(("127.0.0.1", 4173), Handler).serve_forever()
