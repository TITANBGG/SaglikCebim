from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class SpaRequestHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if Path(path).exists():
            return super().send_head()

        if "." not in Path(self.path).name:
            self.path = "/index.html"
            return super().send_head()

        return super().send_head()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a built SPA with index.html fallback.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=5173, type=int)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()

    handler = lambda *handler_args, **handler_kwargs: SpaRequestHandler(
        *handler_args,
        directory=args.directory,
        **handler_kwargs,
    )
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving SPA on http://{args.host}:{args.port} from {args.directory}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
