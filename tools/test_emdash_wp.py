"""Tests for emdash-wp against a local mock WP REST API."""
import http.server
import json
import os
import subprocess
import threading
import unittest

TOOL = os.path.join(os.path.dirname(__file__), "emdash-wp.py")
POSTS = [{"id": 7, "date": "2026-11-20T00:00:00", "status": "publish",
          "title": {"rendered": "Hello"}, "link": "https://x.test/?p=7"}]


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/wp-json/wp/v2/posts"):
            if self.headers.get("Authorization") != "Basic dXNlcjpwYXNz":
                return self._send({"message": "unauthorized"}, 401)
            return self._send(POSTS)
        return self._send({}, 404)

    def do_POST(self):
        if self.path == "/wp-json/wp/v2/posts":
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
            return self._send({"id": 8, "link": "https://x.test/?p=8",
                                "title": data.get("title")}, 201)
        return self._send({}, 404)


class TestWP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    def run_tool(self, *args, fname=None):
        env = dict(os.environ, WP_SITE=f"http://127.0.0.1:{self.port}",
                   WP_USER="user", WP_APP_PASSWORD="pass")
        if fname:
            with open(fname, "w") as f:
                f.write("# Draft\n\nbody text")
        return subprocess.run(["python3", TOOL, *args], capture_output=True,
                              text=True, env=env, timeout=30)

    def test_list(self):
        r = self.run_tool("list")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Hello", r.stdout)

    def test_publish(self):
        r = self.run_tool("publish", "/tmp/wp-draft.md", "--title", "T", "--status", "draft", fname="/tmp/wp-draft.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("https://x.test/?p=8", r.stdout)


if __name__ == "__main__":
    unittest.main()
