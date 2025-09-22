import socket
from unittest.mock import patch

import pytest

from ip import get_local_ip
from ip import main as ip_main


def test_get_local_ip_success() -> None:
    """Testa se get_local_ip retorna o IP correto com socket.gethostbyname mockado."""

    mock_ip: str = "192.168.0.100"  # ip arbitrario

    with patch("socket.gethostbyname", return_value=mock_ip):
        ip: str = get_local_ip()
        assert ip == mock_ip

        # Certifica que gethostbyname foi chamado com o argumento certo
        socket.gethostbyname.assert_called_once_with(socket.gethostname())


def test_get_local_ip_failure() -> None:
    """Testa se get_local_ip levanta RuntimeError quando socket falha."""

    with patch("socket.gethostbyname", side_effect=socket.error("rede inacessível")):
        with pytest.raises(RuntimeError, match="Host não pode ser obtido"):
            get_local_ip()


def test_main_success(capsys: pytest.CaptureFixture) -> None:
    """Testa a função main() com IP mockado."""

    with patch("ip.get_local_ip", return_value="10.0.0.1"):
        ip_main()
        captured = capsys.readouterr()
        assert "10.0.0.1" in captured.out
        assert captured.err == ""


def test_main_failure(capsys: pytest.CaptureFixture) -> None:
    """Testa a função main() quando get_local_ip falha."""

    with patch("ip.get_local_ip", side_effect=RuntimeError("Erro simulado")):
        with pytest.raises(SystemExit) as sys_exit:
            ip_main()
        assert sys_exit.value.code == 1

        captured = capsys.readouterr()
        assert "erro: Erro simulado" in captured.err
