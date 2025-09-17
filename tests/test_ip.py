from unittest.mock import MagicMock, patch

import pytest

from ip import get_local_ip
from ip import main as ip_main


def test_get_local_ip_success() -> None:
    """Testa se get_local_ip retorna o IP correto com socket mockado."""
    mock_socket: MagicMock = MagicMock()
    mock_socket.getsockname.return_value = ("192.168.0.100", 12345)

    with patch("ip.socket", return_value=mock_socket):
        ip: str = get_local_ip()
        assert ip == "192.168.0.100"
        mock_socket.connect.assert_called_once_with(("8.8.8.8", 80))
        mock_socket.close.assert_called_once()


def test_get_local_ip_failure() -> None:
    """Testa se get_local_ip levanta RuntimeError quando socket falha."""
    mock_socket: MagicMock = MagicMock()
    mock_socket.connect.side_effect = OSError("rede inacessível")

    with patch("ip.socket", return_value=mock_socket):
        with pytest.raises(RuntimeError, match="Host não pode ser obtido"):
            get_local_ip()
        mock_socket.close.assert_called_once()


def test_main_success(monkeypatch, capsys) -> None:
    """Testa a função main() com IP mockado."""
    mock_socket: MagicMock = MagicMock()
    mock_socket.getsockname.return_value = ("10.0.0.1", 12345)
    monkeypatch.setattr("ip.socket", lambda *args, **kwargs: mock_socket)

    ip_main()
    captured = capsys.readouterr()
    assert "10.0.0.1" in captured.out
    assert captured.err == ""


def test_main_failure(monkeypatch, capsys) -> None:
    """Testa a função main() quando get_local_ip falha."""

    def mock_socket_fail(*args, **kwargs) -> MagicMock:
        magic_mock: MagicMock = MagicMock()
        magic_mock.connect.side_effect = OSError("rede inacessível")
        return magic_mock

    with patch("ip.socket", mock_socket_fail):
        with pytest.raises(SystemExit) as sys_exit:
            ip_main()
        assert sys_exit.value.code == 1
