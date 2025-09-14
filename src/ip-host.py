import socket
from sys import stderr

soc: socket.socket = socket.socket(family=socket.AF_INET, #IPv4
                                    type=socket.SOCK_DGRAM) # UDP

try:
    soc.connect(("8.8.8.8", 80)) # conexao teste ao dns da google
    ip: str = soc.getsockname()[0]

    print(f"USE ESSE IP PARA ACESSAR OS SERVIDORES: {ip}\n")
except:
    print("erro: host nao pode ser obtido", file=stderr)
    exit(1)
finally:
    soc.close()
