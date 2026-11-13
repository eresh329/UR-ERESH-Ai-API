
import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from google import genai


class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(
            json.dumps(data, ensure_ascii=False).encode("utf-8")
        )

    def process_request(self, message, api_key):
        if not api_key:
            return self.send_json(401, {
                "status": False,
                "error": "API key is required"
            })

        if api_key != os.environ.get("API_ACCESS_KEY"):
            return self.send_json(403, {
                "status": False,
                "error": "Invalid API key"
            })

        if not message or not message.strip():
            return self.send_json(400, {
                "status": False,
                "error": "Message is required"
            })

        try:
            client = genai.Client(
                api_key=os.environ["GEMINI_API_KEY"]
            )

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=message
            )

            return self.send_json(200, {
                "status": True,
                "creator": "YOUR_NAME",
                "model": "Gemini",
                "response": response.text
            })

        except Exception as e:
            return self.send_json(500, {
                "status": False,
                "error": str(e)
            })

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)

        key = params.get("key", [None])[0]
        message = params.get("message", [None])[0]

        self.process_request(message, key)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")

            key = self.headers.get("X-API-Key")
            if not key:
                key = data.get("key")

            self.process_request(data.get("message"), key)

        except Exception:
            self.send_json(400, {
                "status": False,
                "error": "Invalid JSON request"
            })
