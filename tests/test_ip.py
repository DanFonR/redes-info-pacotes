from unittest.mock import MagicMock, patch

import pytest

from ip import get_local_ip, main


def test_get_local_ip_success():
    """Testa se get_local_ip retorna o IP correto com socket mockado."""
    mock_socket = MagicMock()
    mock_socket.getsockname.return_value = ("192.168.0.100", 12345)

    with patch("socket.socket", return_value=mock_socket):
        ip = get_local_ip()
        assert ip == "192.168.0.100"
        mock_socket.connect.assert_called_once_with(("8.8.8.8", 80))
        mock_socket.close.assert_called_once()


def test_get_local_ip_failure():
    """Testa se get_local_ip levanta RuntimeError quando socket falha."""
    mock_socket = MagicMock()
    mock_socket.connect.side_effect = OSError("rede inacessível")

    with patch("socket.socket", return_value=mock_socket):
        with pytest.raises(RuntimeError, match="Host não pode ser obtido"):
            get_local_ip()
        mock_socket.close.assert_called_once()


def test_main_success(monkeypatch, capsys):
    """Testa a função main() com IP mockado."""
    mock_socket = MagicMock()
    mock_socket.getsockname.return_value = ("10.0.0.1", 12345)
    monkeypatch.setattr("socket.socket", lambda *args, **kwargs: mock_socket)

    main()
    captured = capsys.readouterr()
    assert "10.0.0.1" in captured.out
    assert captured.err == ""


def test_main_failure(monkeypatch, capsys):
    """Testa a função main() quando get_local_ip falha."""

    def mock_socket_fail(*args, **kwargs):
        m = MagicMock()
        m.connect.side_effect = OSError("rede inacessível")
        return m

    monkeypatch.setattr("socket.socket", mock_socket_fail)

    with pytest.raises(SystemExit) as e:
        main()
    captured = capsys.readouterr()
    assert "Host não pode ser obtido" in captured.err
    assert e.value.code == 1
