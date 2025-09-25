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
    logging.info("Execução interrompida manualmente")
    exit()


def main() -> None:
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
