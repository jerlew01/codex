import os
import socket
import select
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error

class SimpleHTTPProxyHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_CONNECT(self):
        host, _, port = self.path.partition(':')
        port = int(port) if port else 443
        try:
            remote = socket.create_connection((host, port))
        except Exception:
            self.send_error(502)
            return
        self.send_response(200, 'Connection Established')
        self.end_headers()
        sockets = [self.connection, remote]
        while True:
            r, _, _ = select.select(sockets, [], [])
            if self.connection in r:
                data = self.connection.recv(8192)
                if not data:
                    break
                remote.sendall(data)
            if remote in r:
                data = remote.recv(8192)
                if not data:
                    break
                self.connection.sendall(data)
        remote.close()

    def do_GET(self):
        self._proxy_request('GET')

    def do_POST(self):
        self._proxy_request('POST')

    def _proxy_request(self, method):
        url = self.path
        if not url.startswith('http'):
            url = f'http://{self.headers["Host"]}{self.path}'
        try:
            data = None
            if method == 'POST':
                length = int(self.headers.get('Content-Length', 0))
                data = self.rfile.read(length) if length else None
            req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() == 'transfer-encoding' and v.lower() == 'chunked':
                        continue
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except Exception:
            self.send_error(502)


def run_server():
    port = int(os.getenv('PROXY_PORT', '8080'))
    with HTTPServer(('127.0.0.1', port), SimpleHTTPProxyHandler) as httpd:
        print(f'Simple proxy listening on 127.0.0.1:{port}')
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
