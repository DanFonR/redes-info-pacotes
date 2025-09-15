# EXECUTE COMO SUPERUSUARIO/ADMINISTRADOR
# NO WINDOWS: CERTIFIQUE-SE QUE NPCAP ESTA INSTALADO

from scapy.all import sniff, PacketList
from datetime import datetime
from collections import defaultdict
from sys import stderr
from os import sep
import logging as log
import csv
from signal import signal, SIGINT, Signals
from ip_host import get_ip

# Tipagem
from _csv import Writer
from scapy.layers.inet import IP
from typing import TextIO
from types import FrameType

SRCPATH: str = __file__[:__file__.rindex(sep)]
PATH: str = SRCPATH[:SRCPATH.rindex(sep)]

CSV_SAIDA: str = f"{PATH + sep}netlog.csv"
LOG_SAIDA: str = f"{PATH + sep}netlog_stat.log"
PROTOCOLOS: dict[int, str] = { # Da tabela IANA
	1: "ICMP",
	2: "IGMP",
	4: "IPV4",
	6: "TCP",
	17: "UDP",
	28: "IRTP",
	41: "IPV6",
	58: "IPV6-ICMP"
}

def hora() -> str:
	"""
	Obtem data e hora atual e a retorna em formato 
	YYYY-MM-DD HH:MM:SS
	"""

	data: datetime = datetime.now()

	return f"{data:%Y-%m-%d %H:%M:%S}"

def sigint_handler(sig: Signals, frame: FrameType|None):
	global interrompeu
	interrompeu = True

pacotes: PacketList
csv_arquivo: TextIO
bytes_ip: defaultdict[tuple[IP, str], dict[str, int]]
writer: Writer

# Configuracoes iniciais para logging
log.basicConfig(level=log.INFO,
				style='{', format="([{levelname}] - {asctime}): {message}",
				handlers=(log.FileHandler(LOG_SAIDA, encoding="utf-8"),
						log.StreamHandler()))

# Inicializa arquivo com header (newline='' conforme documentacao do modulo csv)
with open(CSV_SAIDA, "w", newline='') as csv_arquivo:
	writer = csv.writer(csv_arquivo)
	header: list[str] = [
		"data_hora", "ip", "protocolo",
		"bytes_enviados", "bytes_recebidos",
		"destino_rementente"
    ]

	writer.writerow(header)

volta: int = 1
interrompeu: bool = False

while True:
	try:
		# Captura pacotes por 5 segundos
		pacotes = sniff(timeout=5)
	except Exception as erro:
		log.warning("Erro durante captura, "
			  		f"pulando... (Erro: {type(erro).__name__}: {erro})")
		continue

	signal(SIGINT, sigint_handler)

	if interrompeu:
		print("Interrompendo...", file=stderr)
		log.info("Execução interrompida manualmente")
		del pacotes
		exit(0)

	bytes_ip: defaultdict = defaultdict(lambda: {"enviado": 0, "recebido": 0})

	for pacote in pacotes:
		if IP not in pacote:
			continue

		ip: IP = pacote[IP]
		protocolo: str = PROTOCOLOS.get(ip.proto, "Outro")
		tamanho: int = len(pacote)

		# Valores de bytes enviados e recebidos, por IP e protocolo
		bytes_ip[(ip.src, protocolo)]["enviado"] += tamanho
		bytes_ip[(ip.dst, protocolo)]["recebido"] += tamanho

	with open(CSV_SAIDA, "a", newline='') as csv_arquivo:
		ip_bytes: IP
		protocolo: str
		tipo_ip: str
		valores: dict[str, int]
		writer = csv.writer(csv_arquivo)
		hora_atual: str = hora()

		for (ip_bytes, protocolo), valores in bytes_ip.items():
			if ip_bytes == ip.src:
				tipo_ip = "remetente"
			else:
				tipo_ip = "destino"

			linha: list[str] = [
				hora_atual, ip_bytes, protocolo,
				valores["enviado"], valores["recebido"],
				tipo_ip
            ]

			writer.writerow(linha)

	log.info(f"iteracao {volta} concluida")

	volta += 1
