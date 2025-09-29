"""
Módulo principal do sistema de captura e monitoramento de rede.
"""

import logging
import os
from signal import SIGINT, signal
from threading import Thread
from typing import NoReturn

from netlog import NetLogger
from servers import Server

SRCPATH: str = os.path.dirname(__file__)
PATH: str = os.path.dirname(SRCPATH)

CSV_SAIDA: str = os.path.join(PATH, "netlog.csv")
LOG_SAIDA: str = os.path.join(PATH, "netlog_stat.log")


def sigint_handler() -> NoReturn:
    """
    Função chamada quando o programa recebe um sinal SIGINT (CTRL+C).

    Efeitos colaterais:
        - Registra no log a interrupção.
        - Encerra o processo imediatamente.
    """
    logging.info("Execução interrompida manualmente")
    exit()


def main() -> None:
    """
    Função principal do sistema.

    Responsabilidades:
    - Configura o logging (arquivo e console).
    - Registra o handler de interrupção SIGINT.
    - Cria e inicia os threads para:
        * Servidores HTTP/FTP (`Server.start`)
        * Captura de pacotes (`NetLogger.run`)
    - Mantém os threads ativos até o término.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="([{levelname}] - {asctime}): {message}",
        style="{",
        handlers=[
            logging.FileHandler(filename=LOG_SAIDA, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    signal(SIGINT, sigint_handler)

    servidores: Server = Server()
    logger: NetLogger = NetLogger(CSV_SAIDA)

    thread_servidores: Thread = Thread(target=servidores.start, daemon=True)
    thread_logger: Thread = Thread(target=logger.run, daemon=True)

    thread_logger.start()
    thread_servidores.start()

    thread_logger.join()
    thread_servidores.join()


if __name__ == "__main__":
    main()
