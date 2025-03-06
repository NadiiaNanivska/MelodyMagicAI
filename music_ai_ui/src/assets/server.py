import http.server
import socketserver
from urllib.parse import unquote
import os

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')  # Дозволяє доступ з будь-якого домену
        super().end_headers()

    def do_GET(self):
        # Перевіряємо, чи це запит на ваш локальний файл
        if self.path == '/output.midi':
            self.path = 'output.midi'  # Вказуємо точний файл, який потрібно відправити
        return super().do_GET()

PORT = 8000

Handler = CORSRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

print(f"Serving at port {PORT}")
httpd.serve_forever()
