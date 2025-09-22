"""
Módulo para obter o IP local da máquina.

O IP retornado é o utilizado para acessar a internet/servidores.
"""

import socket
import sys


def get_local_ip() -> str:
    """
    Retorna o endereço IP local da máquina,
    usando o nome do host da máquina.

    Essa função usa gethostname() para pegar o nome do host
    e gethostbyname() para obter o IP correspondente.

    Returns:
        str: Endereço IP local da máquina.

    Raises:
        RuntimeError: Se não for possível determinar o IP local.
    """

    try:
        return socket.gethostbyname(socket.gethostname())
    except socket.error as socket_error:
        raise RuntimeError("Host não pode ser obtido") from socket_error


def main() -> None:
    """
    Função principal para execução do módulo como script.

    Obtém o IP local e imprime no console. Caso ocorra erro, escreve no stderr
    e encerra o programa com código de erro 1.
    """

    try:
        ip: str = get_local_ip()
        print(f"USE ESSE IP PARA ACESSAR OS SERVIDORES: {ip}\n")
    except RuntimeError as runtime_error:
        print(f"erro: {runtime_error}", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
