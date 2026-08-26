import base64
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

OUT = '/workspace/shots'

class H(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            data = json.loads(body)
            name = data['name']
            b64 = data['data']
            if ',' in b64:
                b64 = b64.split(',')[1]
            raw = base64.b64decode(b64)
            with open(os.path.join(OUT, name), 'wb') as f:
                f.write(raw)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(('saved ' + name + ' ' + str(len(raw)) + ' bytes').encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(str(e).encode())

if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 8124), H).serve_forever()
