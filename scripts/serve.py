"""Serve the Pages project under its deployment prefix, without dependencies."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/feucht':
            self.send_response(301)
            self.send_header('Location', '/feucht/')
            self.end_headers()
            return
        if not path.startswith('/feucht/'):
            self.send_error(404)
            return
        self.path = self.path[len('/feucht'):]
        super().do_GET()
if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args()
    root = Path(__file__).resolve().parents[1] / 'site'
    ThreadingHTTPServer(('127.0.0.1', args.port),partial(Handler,directory=str(root))).serve_forever()
