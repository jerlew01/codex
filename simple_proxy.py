import os
import socket
import select
import socketserver
from http.server import BaseHTTPRequestHandler
import urllib.request

class ProxyRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_CONNECT(self):
        host, port = self.path.split(':')
        try:
            port = int(port)
        except ValueError:
            self.send_error(400, 'Invalid port')
            return
        try:
            remote = socket.create_connection((host, port))
        except OSError as e:
            self.send_error(502, str(e))
            return

        self.send_response(200, 'Connection Established')
        self.end_headers()

        sockets = [self.connection, remote]
        while True:
            rlist, _, _ = select.select(sockets, [], [])
            if self.connection in rlist:
                data = self.connection.recv(8192)
                if not data:
                    break
                remote.sendall(data)
            if remote in rlist:
                data = remote.recv(8192)
                if not data:
                    break
                self.connection.sendall(data)
        remote.close()
        self.connection.close()

    def do_GET(self):
        self._proxy_request()

    def do_POST(self):
        self._proxy_request()

    def do_PUT(self):
        self._proxy_request()

    def do_DELETE(self):
        self._proxy_request()

    def _proxy_request(self):
        url = self.path
        if not url.startswith('http'):
            url = f"http://{self.headers['Host']}{url}"
        data = None
        if 'Content-Length' in self.headers:
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'proxy-connection'}
        req = urllib.request.Request(url, data=data, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() != 'transfer-encoding':
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
        except Exception as e:
            self.send_error(502, str(e))


def run():
    port = int(os.environ.get('PROXY_PORT', '8080'))
    with socketserver.ThreadingTCPServer(('127.0.0.1', port), ProxyRequestHandler) as httpd:
        print(f"Simple proxy listening on 127.0.0.1:{port}")
        httpd.serve_forever()


if __name__ == '__main__':
    run()
