"""
NetLogger - Captura de pacotes de rede e estatísticas em CSV e log.

Requer privilégios de administrador/root.
No Windows, certifique-se que o Npcap está instalado.
"""

import csv
import logging
from _csv import Writer
from collections import defaultdict
from datetime import datetime
from signal import SIGINT, signal
from sys import stderr
from types import FrameType

from scapy.all import sniff, Packet, PacketList
from scapy.layers.inet import IP

PROTOCOLOS: dict[int, str] = {
    # Tabela de protocolos IANA (apenas alguns exemplos)
    1: "ICMP",
    2: "IGMP",
    4: "IPV4",
    6: "TCP",
    17: "UDP",
    28: "IRTP",
    41: "IPV6",
    58: "IPV6-ICMP",
}

def hora() -> str:
    """
    Retorna a data e hora atual formatada como 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        str: Data e hora atual formatada.
    """

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class NetLogger:
    """
    Classe para captura de pacotes de rede e registro em CSV e log.

    Attributes:
        csv_path (str): Caminho do arquivo CSV de saída.
        log_path (str): Caminho do arquivo de log.
        interrompeu (bool): Flag para indicar interrupção manual.
        numero_iteracao (int): Contador de iterações.
    """

    def __init__(self, csv_path: str, log_path: str):
        """
        Inicializa o NetLogger, configurando CSV e log.

        Args:
            csv_path (str): Caminho do arquivo CSV de saída.
            log_path (str): Caminho do arquivo de log.
        """

        self.csv_path = csv_path
        self.log_path = log_path
        self.interrompeu = False
        self.numero_iteracao = 1

        logging.basicConfig(
            level=logging.INFO,
            format="([{levelname}] - {asctime}): {message}",
            style="{",
            handlers=[
                logging.FileHandler(filename=log_path, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )

        self._setup_csv()

        # Captura CTRL+C
        signal(SIGINT, self.__sigint_handler)

    def __sigint_handler(self, sig: int, frame: FrameType) -> None:
        """
        Handler para sinal SIGINT (CTRL+C) para interrupção manual.

        Args:
            sig (int): Número do sinal.
            frame: Frame do sinal (não usado).
        """

        self.interrompeu = True

    def _setup_csv(self) -> None:
        """
        Inicializa o arquivo CSV com cabeçalho.
        """

        with open(self.csv_path, "w", newline="") as f:
            writer: Writer = csv.writer(f)
            writer.writerow(
                [
                    "data_hora",
                    "ip",
                    "protocolo",
                    "bytes_enviados",
                    "bytes_recebidos",
                    "tipo",
                ]
            )

    def processa_pacotes(self, timeout: int = 5) -> None:
        """
        Captura pacotes por um período e registra estatísticas em CSV e log.

        Args:
            timeout (int, optional):
            Tempo em segundos para captura de pacotes. 5 por padrão.
        """

        pacote: Packet
        pacotes: PacketList = sniff(timeout=timeout)
        bytes_ip: defaultdict = defaultdict(lambda: {"enviado": 0,
                                                     "recebido": 0})

        for pacote in pacotes:
            if IP not in pacote:
                continue

            ip: IP = pacote[IP]
            protocolo = PROTOCOLOS.get(ip.proto, "Outro")
            tamanho = len(pacote)
            bytes_ip[(ip.src, protocolo)]["enviado"] += tamanho
            bytes_ip[(ip.dst, protocolo)]["recebido"] += tamanho

        hora_atual: str = hora()

        with open(self.csv_path, "a", newline="") as f:
            writer: Writer = csv.writer(f)

            for (ip_end, protocolo), valores in bytes_ip.items():
                tipo = "remetente" if ip_end == ip.src else "destino"
                writer.writerow(
                    [
                        hora_atual,
                        ip_end,
                        protocolo,
                        valores["enviado"],
                        valores["recebido"],
                        tipo,
                    ]
                )

        logging.info(f"Iteração {self.numero_iteracao} concluída")
        self.numero_iteracao += 1

    def run(self) -> None:
        """
        Executa o loop de captura contínua até interrupção manual.
        """

        while not self.interrompeu:
            try:
                self.processa_pacotes()
            except Exception as ex:
                logging.warning(
                    f"Erro durante captura: {type(ex).__name__}: {ex}"
                )

        print("Interrompendo...", file=stderr)
        logging.info("Execução interrompida manualmente")

if __name__ == "__main__":
    import os

    SRCPATH: str = os.path.dirname(__file__)
    PATH: str = os.path.dirname(SRCPATH)

    CSV_SAIDA: str = os.path.join(PATH, "netlog.csv")
    LOG_SAIDA: str = os.path.join(PATH, "netlog_stat.log")

    logger: NetLogger = NetLogger(CSV_SAIDA, LOG_SAIDA)
    logger.run()
