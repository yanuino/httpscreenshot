import shutil
import socket
import socketserver
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from io import BytesIO
import pyautogui
import base64

PORT = 8099

def pil_base64(image):
  img_buffer = BytesIO()
  image.save(img_buffer, format='PNG')
  byte_data = img_buffer.getvalue()
  base64_str = base64.b64encode(byte_data)
  return base64_str

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        
        print(self.requestline)

        if( self.requestline.find("GET /favicon.ico") != -1 ):
            # Si la requête demande l'icone de la page, ne fait rien
            self.send_error(404)
            return

        # Capture
        im = pyautogui.screenshot()
        # Conversion de l'image en Base64 (texte pouvant être intégré dans une page web)
        imbase64 = pil_base64(im)
        # Génération code HTML
        html = f"""<html><head><style>img.full {{  max-width: 100%;  height: auto; }} </style><body><img <img src="data:image/png;base64,{imbase64.decode('utf-8')}" class="full" /><script type="text/javascript">setInterval(function(){{ location.reload(); }}, 5000);</script></body></head></html>"""
        
        # Envoi de la réponse
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", len(html))
        self.end_headers()
        shutil.copyfileobj(BytesIO(html.encode('utf-8')), self.wfile)

    def handle(self):
        # Superseding the handle function for error handling
        try:
            BaseHTTPRequestHandler.handle(self)
        except socket.error as e:
            print(f"Connection error: {e}")
            pass

    # def finish(self,*args,**kw):
    #     try:
    #         if not self.wfile.closed:
    #             self.wfile.flush()
    #             self.wfile.close()
    #     except socket.error:
    #         pass
    #     self.rfile.close()

    #     #Don't call the base class finish() method as it does the above
    #     #return SocketServer.StreamRequestHandler.finish(self)

def run_http_server(port=8080):
    with socketserver.ThreadingTCPServer(("", port), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        finally:
            httpd.server_close()


if __name__ == "__main__":
    print("Running HTTP server on port ", PORT)
    run_http_server(PORT)