import socket
from sys import stderr

def get_ip() -> str:
    soc: socket.socket = socket.socket(family=socket.AF_INET, #IPv4
                                        type=socket.SOCK_DGRAM) # UDP
    try:
        soc.connect(("8.8.8.8", 80)) # conexao teste ao dns da google
        ip: str = soc.getsockname()[0]
        return ip
    except:
        return ""
    finally:
        soc.close()

if __name__ == "__main__":
    from sys import stderr

    IP: str = get_ip()

    if IP == "":
        print("erro: host nao pode ser obtido", file=stderr)
        exit(1)

    print(f"USE {IP}:8000 PARA ACESSAR O SERVIDOR HTTP", file=stderr)
    print(f"USE {IP}:2121 PARA ACESSAR O SERVIDOR FTP\n", file=stderr)
