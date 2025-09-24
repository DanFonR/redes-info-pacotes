import os
import logging
from threading import Lock, Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from time import sleep

LOCK: Lock = Lock()

ip_set: set[str] = set()

class LoggingHTTPHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        logging.info(f"IP {client_ip} conectado via HTTP")

        # Adiciona ao conjunto de IPs com Lock, para evitar race conditions
        with LOCK:
            ip_set.add(client_ip)

        super().do_GET()

class LoggingFTPHandler(FTPHandler):
    def on_connect(self, username: str) -> None:
        client_ip = self.remote_ip
        logging.info(f"IP {client_ip} conectado via FTP")

        with LOCK:
            ip_set.add(client_ip)

class Server:
    http_port: int
    ftp_port: int
    http_thread: Thread|None
    ftp_thread: Thread|None

    def __init__(self, http_port: int = 8000, ftp_port: int = 2121):
        self.http_port = http_port
        self.ftp_port = ftp_port
        self.http_thread = None
        self.ftp_thread = None

    def start_http_server(self):
        handler: LoggingHTTPHandler = LoggingHTTPHandler
        server: HTTPServer = HTTPServer(('0.0.0.0', self.http_port), handler)

        logging.info(f"Inicializando servidor HTTP na porta {self.http_port}")
        server.serve_forever()

    def start_ftp_server(self):
        authorizer: DummyAuthorizer = DummyAuthorizer()

        # Permite acesso anonimo
        authorizer.add_anonymous(os.getcwd(), perm='elradfmw')

        handler: LoggingFTPHandler = LoggingFTPHandler
        handler.authorizer = authorizer

        server = FTPServer(('0.0.0.0', self.ftp_port), handler)

        logging.info(f"Inicializando servidor FTP na porta {self.ftp_port}")
        server.serve_forever()

    def start(self):
        self.http_thread = Thread(target=self.start_http_server, daemon=True)
        self.ftp_thread = Thread(target=self.start_ftp_server, daemon=True)

        self.http_thread.start()
        self.ftp_thread.start()

        self.http_thread.join()
        self.ftp_thread.join()

def get_ips() -> set[str]:
    """
    Retorna conjunto de IPs colhidos pelos servidores
    """
    return ip_set
