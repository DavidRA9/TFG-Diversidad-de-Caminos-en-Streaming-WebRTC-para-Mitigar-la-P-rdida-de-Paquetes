from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Evitar el caché para los segmentos
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')

        # Permitir CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

# Usar 0.0.0.0 para aceptar conexiones desde cualquier IP
host = '0.0.0.0'
port = 1234

httpd = HTTPServer((host, port), CORSRequestHandler)

# Obtener la IP local de la máquina
local_ip = socket.gethostbyname(socket.gethostname())

print(f"✅ Serving at http://{local_ip}:{port}")
httpd.serve_forever()
