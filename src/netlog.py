"""
NetLogger - Captura de pacotes de rede e gera estatísticas em CSV e log.

Funcionalidades principais:
- Captura pacotes de todas as interfaces de rede usando Scapy.
- Filtra apenas pacotes envolvendo os IPs coletados
  (servidores locais e conexões HTTP/FTP).
- Calcula estatísticas de bytes enviados e recebidos por IP e protocolo.
- Registra os resultados em um arquivo CSV e também em log.
- Suporta interrupção manual via CTRL+C (SIGINT).

Requisitos:
- Privilégios de administrador/root.
- No Windows, é necessário ter o Npcap instalado.
- Integra com `servers.get_ips` para incluir IPs conectados aos
  servidores locais.
"""

import csv
import logging
import sys
from collections import defaultdict
from datetime import datetime
from signal import SIGINT, signal
from types import FrameType

from _csv import Writer
from scapy.all import Packet, PacketList, get_if_list, sniff
from scapy.layers.inet import IP, TCP

from ip import get_local_ip
from servers import get_ips

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


def http_ftp(portas: tuple[int, int], http: int = 8000, ftp: int = 2121) -> str:
    """
    Converte ``8000`` para ``"HTTP"`` e ``2121`` para ``"FTP"``,
    para uso no .csv
    """

    if http in portas:
        return "HTTP"
    elif ftp in portas:
        return "FTP"
    else:
        return "Outro"


def hora() -> str:
    """
    Retorna a data e hora atual formatada como 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        str: Data e hora atual formatada.
    """

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class NetLogger:
    """
    Captura pacotes de rede e registra estatísticas em CSV e log.

    Fluxo:
    - Inicializa o arquivo CSV com cabeçalho.
    - Entra em um loop contínuo (`run`) capturando pacotes em intervalos.
    - Processa pacotes para atualizar estatísticas por IP/protocolo.
    - Escreve os resultados no CSV e no log a cada iteração.
    - Interrompido manualmente com CTRL+C.

    Attributes:
        csv_path (str): Caminho do arquivo CSV de saída.
        interrompeu (bool): Indica se a execução foi interrompida manualmente.
        numero_iteracao (int): Contador de iterações de captura.
        conexoes (set[str]): Conjunto de IPs locais ou conectados a servidores.
    """

    def __init__(self, csv_path: str, portas_proibidas: tuple[int] = (8501,)):
        """
        Inicializa o arquivo CSV de saída com o cabeçalho padrão.

        Colunas:
            - data_hora
            - ip
            - protocolo
            - bytes_enviados
            - bytes_recebidos
            - tipo (remetente/destino)
        """

        self.csv_path: str = csv_path
        self.interrompeu: bool = False
        self.numero_iteracao: int = 1
        self.conexoes: set[str]
        self.portas_proibidas: tuple[int] = portas_proibidas

        try:
            self.conexoes = {get_local_ip()}
        except RuntimeError:
            print("erro ao obter ip do servidor", file=sys.stderr)
            exit(1)

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

        Para cada iteração:
        - Captura pacotes em todas as interfaces por `timeout` segundos.
        - Filtra pacotes IP que envolvam os IPs conhecidos
          (conexões + IP local).
        - Acumula bytes enviados/recebidos por IP e protocolo.
        - Escreve estatísticas no CSV com timestamp.

        Args:
            timeout (int, optional): Tempo em segundos \
            para captura (padrão: 5).
        """

        pacote: Packet
        bytes_ip: defaultdict[tuple[str, str], dict[str, int]]
        interfaces: list[str] = get_if_list()
        pacotes: PacketList = sniff(timeout=timeout, iface=interfaces)
        bytes_ip = defaultdict(lambda: {"enviado": 0, "recebido": 0})

        self.conexoes |= get_ips()  # atualiza lista de IPs conectados

        for pacote in pacotes:
            # evita pacotes com ICMP ou IGMP, por exemplo
            if IP not in pacote or TCP not in pacote:
                continue

            ip: IP = pacote[IP]
            tcp: TCP = pacote[TCP]
            if (ip.src not in self.conexoes or ip.dst not in self.conexoes) or (
                tcp.sport in self.portas_proibidas or tcp.dport in self.portas_proibidas
            ):
                continue

            conn_protocolo: str = http_ftp((tcp.sport, tcp.dport))
            tamanho = len(pacote)
            bytes_ip[(ip.src, conn_protocolo)]["enviado"] += tamanho
            bytes_ip[(ip.dst, conn_protocolo)]["recebido"] += tamanho

        hora_atual: str = hora()

        with open(self.csv_path, "a", newline="") as f:
            ip_end: str
            protocolo: str
            writer: Writer = csv.writer(f)

            for (ip_end, protocolo), valores in bytes_ip.items():
                tipo: str = "remetente" if ip_end == ip.src else "destino"
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

        - Chama `processa_pacotes` em loop.
        - Em caso de erro durante a captura, registra no log e continua.
        - Sai apenas quando `SIGINT` (CTRL+C) é recebido.
        """

        msg: str

        while not self.interrompeu:
            try:
                self.processa_pacotes()
            except Exception as ex:
                msg = f"Erro durante captura: {type(ex).__name__}: {ex}"
                logging.warning(msg)

        print("Interrompendo...", file=sys.stderr)
        logging.info("Execução interrompida manualmente")


if __name__ == "__main__":
    import os

    SRCPATH: str = os.path.dirname(__file__)
    PATH: str = os.path.dirname(SRCPATH)

    CSV_SAIDA: str = os.path.join(PATH, "netlog.csv")
    LOG_SAIDA: str = os.path.join(PATH, "netlog_stat.log")

    logger: NetLogger = NetLogger(CSV_SAIDA)
    logger.run()
