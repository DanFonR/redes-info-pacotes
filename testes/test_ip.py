import socket
from unittest.mock import patch

import pytest

from ip import get_local_ip
from ip import main as ip_main


def test_get_local_ip_success() -> None:
    """
    Testa se get_local_ip retorna o IP correto
    com socket.gethostbyname mockado.
    """

    mock_ip: str = "192.168.0.100"  # ip arbitrario

    with patch("socket.gethostbyname", return_value=mock_ip):
        ip: str = get_local_ip()
        assert ip == mock_ip

        # Certifica que gethostbyname foi chamado com o argumento certo
        socket.gethostbyname.assert_called_once_with(socket.gethostname())


def test_get_local_ip_failure() -> None:
    """
    Testa se get_local_ip levanta RuntimeError quando socket falha.
    """

    efeito: OSError = socket.error("rede inacessível")

    with patch("socket.gethostbyname", side_effect=efeito):
        with pytest.raises(RuntimeError, match="Host não pode ser obtido"):
            get_local_ip()


def test_main_success(capsys: pytest.CaptureFixture) -> None:
    """
    Testa a função ip.main() com IP mockado.
    """

    mock_ip: str = "10.0.0.1"

    with patch("ip.get_local_ip", return_value=mock_ip):
        ip_main()
        captured = capsys.readouterr()
        assert mock_ip in captured.out
        assert not captured.err


def test_main_failure(capsys: pytest.CaptureFixture) -> None:
    """
    Testa a função main() quando get_local_ip falha.
    """

    efeito: RuntimeError = RuntimeError("Erro simulado")

    with patch("ip.get_local_ip", side_effect=efeito):
        with pytest.raises(SystemExit) as sys_exit:
            ip_main()
        assert sys_exit.value.code == 1

        captured = capsys.readouterr()
        assert "erro: Erro simulado" in captured.err
