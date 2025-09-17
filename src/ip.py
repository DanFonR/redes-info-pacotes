"""
Módulo para obter o IP local da máquina.

O IP retornado é o utilizado para acessar a internet/servidores.
"""

from socket import AF_INET, SOCK_DGRAM, socket
from sys import stderr


def get_local_ip() -> str:
    """
    Retorna o endereço IP local da máquina,
    tentando se conectar a um servidor externo.

    Essa função cria um socket UDP temporário,
    conecta ao DNS público do Google (8.8.8.8)
    para descobrir o IP local que seria usado para comunicação externa.

    Returns:
        str: Endereço IP local da máquina.

    Raises:
        RuntimeError: Se não for possível determinar o IP local.
    """

    # familia de endereco para IPv4 (formato: (endereco, porta)), tipo UDP
    soc: socket = socket(family=AF_INET, type=SOCK_DGRAM)

    try:
        soc.connect(("8.8.8.8", 80))  # conexão teste ao DNS do Google
        return soc.getsockname()[0]
    except OSError as os_error:
        # Captura apenas erros relacionados a socket/rede
        raise RuntimeError("Host não pode ser obtido") from os_error
    finally:
        soc.close()


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
        print(f"erro: {runtime_error}", file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
