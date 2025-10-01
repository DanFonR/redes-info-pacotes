"""
Módulo para obtenção do IP local da máquina.

O IP retornado é o associado ao nome do host (hostname) do sistema,
usando `socket.gethostbyname(socket.gethostname())`.

Observação:
Esse método pode retornar `127.0.0.1` em algumas configurações
onde o hostname está associado ao loopback. É adequado para cenários
simples, mas pode não refletir o IP real usado para acessar a internet.
"""

import socket
import sys


def get_local_ip() -> str:
    """
    Retorna o endereço IP local da máquina, com base no hostname.

    Esse método consulta o nome do host via `socket.gethostname()`
    e resolve o IP correspondente via `socket.gethostbyname()`.

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
    Executa o módulo como script.

    - Obtém o IP local da máquina e imprime no console.
    - Em caso de falha, imprime o erro em stderr e encerra com código 1.
    """

    try:
        ip: str = get_local_ip()
        print(f"USE ESSE IP PARA ACESSAR OS SERVIDORES: {ip}\n")
    except RuntimeError as runtime_error:
        print(f"erro: {runtime_error}", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
