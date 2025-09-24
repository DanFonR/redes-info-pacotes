import os
from netlog import NetLogger
from servers import Server
import logging
from threading import Thread


SRCPATH: str = os.path.dirname(__file__)
PATH: str = os.path.dirname(SRCPATH)

CSV_SAIDA: str = os.path.join(PATH, "netlog.csv")
LOG_SAIDA: str = os.path.join(PATH, "netlog_stat.log")

logging.basicConfig(
    level=logging.INFO,
    format="([{levelname}] - {asctime}): {message}",
    style="{",
    handlers=[
        logging.FileHandler(filename=LOG_SAIDA, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

servidores: Server = Server()
logger: NetLogger = NetLogger(CSV_SAIDA)

thread_servidores: Thread = Thread(target=servidores.start)
thread_logger: Thread = Thread(target=logger.run)

thread_logger.start()
thread_servidores.start()

thread_logger.join()
thread_servidores.join()
