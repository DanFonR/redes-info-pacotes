"""
Módulo de servidores HTTP e FTP com logging e coleta de IPs conectados.

Funcionalidades principais:
- Servidor HTTP: registra cada conexão e adiciona o
  IP do cliente ao conjunto global.
- Servidor FTP: permite conexões anônimas, registra o IP do cliente
  e também o armazena.
- Sincronização: o conjunto de IPs (`ip_set`) é protegido por um `Lock` para
  evitar condições de corrida entre múltiplas threads.
- Classe `Server`: inicializa e gerencia os servidores HTTP e FTP
  em threads separadas.

Uso típico:
    server = Server(http_port=8000, ftp_port=2121)
    server.start()

    # Mais tarde, é possível acessar os IPs conectados:
    ips = get_ips()
"""

import logging
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Lock, Thread

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

LOCK: Lock = Lock()

ip_set: set[str] = set()


class LoggingHTTPHandler(SimpleHTTPRequestHandler):
    """
    Handler HTTP que registra e coleta IPs de clientes conectados.
    """

    def do_GET(self):
        """
        Trata requisições GET:
        - Registra no log o IP do cliente.
        - Armazena o IP no conjunto global, com proteção via Lock.
        - Continua o fluxo normal do SimpleHTTPRequestHandler.
        """
        client_ip = self.client_address[0]
        logging.info(f"IP {client_ip} conectado via HTTP")

        # Adiciona ao conjunto de IPs com Lock, para evitar race conditions
        with LOCK:
            ip_set.add(client_ip)

        super().do_GET()


class LoggingFTPHandler(FTPHandler):
    """
    Handler FTP que registra e coleta IPs de clientes conectados.
    """

    def on_connect(self) -> None:
        """
        Chamado automaticamente quando um cliente FTP se conecta:
        - Registra o IP no log.
        - Armazena o IP no conjunto global, com proteção via Lock.
        """
        client_ip = self.remote_ip
        logging.info(f"IP {client_ip} conectado via FTP")

        with LOCK:
            ip_set.add(client_ip)


class Server:
    """
    Classe responsável por gerenciar servidores HTTP e FTP.

    Atributos:
        http_port (int): Porta do servidor HTTP.
        ftp_port (int): Porta do servidor FTP.
        http_thread (Thread | None): Thread responsável pelo servidor HTTP.
        ftp_thread (Thread | None): Thread responsável pelo servidor FTP.
    """

    http_port: int
    ftp_port: int
    http_thread: Thread | None
    ftp_thread: Thread | None

    def __init__(self, http_port: int = 8000, ftp_port: int = 2121):
        """
        Inicializa a instância do servidor.

        Args:
            http_port (int): Porta para o servidor HTTP (padrão: 8000).
            ftp_port (int): Porta para o servidor FTP (padrão: 2121).
        """
        self.http_port = http_port
        self.ftp_port = ftp_port
        self.http_thread = None
        self.ftp_thread = None

    def start_http_server(self):
        """
        Inicia o servidor HTTP com LoggingHTTPHandler na porta configurada.
        """
        handler: LoggingHTTPHandler = LoggingHTTPHandler
        server: HTTPServer = HTTPServer(("0.0.0.0", self.http_port), handler)

        logging.info(f"Inicializando servidor HTTP na porta {self.http_port}")
        server.serve_forever()

    def start_ftp_server(self):
        """
        Inicia o servidor FTP com LoggingFTPHandler na porta configurada.
        O acesso é anônimo e concedido ao diretório de trabalho atual.
        """
        authorizer: DummyAuthorizer = DummyAuthorizer()

        # Permite acesso anonimo
        authorizer.add_anonymous(os.getcwd(), perm="elradfmw")

        handler: LoggingFTPHandler = LoggingFTPHandler
        handler.authorizer = authorizer

        server = FTPServer(("0.0.0.0", self.ftp_port), handler)

        logging.info(f"Inicializando servidor FTP na porta {self.ftp_port}")
        server.serve_forever()

    def start(self):
        """
        Inicia os servidores HTTP e FTP em threads daemon.
        Os servidores rodam indefinidamente até o processo ser encerrado.
        """
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
