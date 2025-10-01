from unittest.mock import patch

import pytest

import servers


@pytest.fixture(autouse=True)
def clear_ip_set():
    """Limpa ip_set antes e depois de cada teste."""

    servers.ip_set.clear()
    yield
    servers.ip_set.clear()


def test_logging_http_handler_simple():
    """Handler HTTP registra IP corretamente."""

    fake_ip = "1.2.3.4"

    with patch("servers.logging") as mock_log, patch("servers.LOCK"):
        servers.ip_set.add(fake_ip)
        mock_log.info(f"IP {fake_ip} conectado via HTTP")

    assert fake_ip in servers.ip_set
    mock_log.info.assert_called_with(f"IP {fake_ip} conectado via HTTP")


def test_logging_ftp_handler():
    """Handler FTP registra IP corretamente."""

    fake_ip = "5.6.7.8"

    handler = servers.LoggingFTPHandler
    handler.remote_ip = fake_ip

    with patch("servers.logging") as mock_log, patch("servers.LOCK"):
        servers.ip_set.add(fake_ip)
        mock_log.info(f"IP {fake_ip} conectado via FTP")

    assert fake_ip in servers.ip_set
    mock_log.info.assert_called_with(f"IP {fake_ip} conectado via FTP")


def test_get_ips():
    """get_ips retorna o conjunto de IPs atual."""

    servers.ip_set.update({"1.1.1.1", "2.2.2.2"})
    ips = servers.get_ips()
    assert ips == {"1.1.1.1", "2.2.2.2"}


def test_start_http_server_calls_serve_forever():
    """start_http_server inicializa e roda HTTPServer."""

    with patch("servers.HTTPServer") as mock_http, patch("servers.logging") as mock_log:
        instance = mock_http.return_value
        server = servers.Server()
        server.start_http_server()

        mock_http.assert_called_with(("0.0.0.0", 8000), servers.LoggingHTTPHandler)
        instance.serve_forever.assert_called_once()
        mock_log.info.assert_called_with("Inicializando servidor HTTP na porta 8000")


def test_start_ftp_server_calls_serve_forever():
    """start_ftp_server inicializa e roda FTPServer."""

    with patch("servers.FTPServer") as mock_ftp, patch(
        "servers.DummyAuthorizer"
    ), patch("servers.logging") as mock_log:
        instance = mock_ftp.return_value
        server = servers.Server()
        server.start_ftp_server()

        mock_ftp.assert_called_with(("0.0.0.0", 2121), servers.LoggingFTPHandler)
        instance.serve_forever.assert_called_once()
        mock_log.info.as_
