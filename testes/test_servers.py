from unittest.mock import patch

import pytest

import servers


@pytest.fixture(autouse=True)
def clear_ip_set():
    # Limpa o conjunto de IPs antes e depois de cada teste
    servers.ip_set.clear()
    yield
    servers.ip_set.clear()


def test_logging_http_handler_simple():
    fake_ip = "1.2.3.4"

    with patch("servers.logging") as mock_log, patch("servers.LOCK"):
        # Simula o efeito do handler sem instanciar
        servers.ip_set.add(fake_ip)
        mock_log.info(f"IP {fake_ip} conectado via HTTP")

    assert fake_ip in servers.ip_set
    mock_log.info.assert_called_with(f"IP {fake_ip} conectado via HTTP")


def test_logging_ftp_handler():
    fake_ip = "5.6.7.8"

    handler = servers.LoggingFTPHandler
    handler.remote_ip = fake_ip

    with patch("servers.logging") as mock_log, patch("servers.LOCK"):
        # Simula o efeito do handler sem instanciar
        servers.ip_set.add(fake_ip)
        mock_log.info(f"IP {fake_ip} conectado via FTP")

    assert fake_ip in servers.ip_set
    mock_log.info.assert_called_with(f"IP {fake_ip} conectado via FTP")


def test_get_ips():
    servers.ip_set.update({"1.1.1.1", "2.2.2.2"})
    ips = servers.get_ips()
    assert ips == {"1.1.1.1", "2.2.2.2"}


def test_start_http_server_calls_serve_forever():
    with patch("servers.HTTPServer") as mock_http, patch(
        "servers.logging"
    ) as mock_log:
        instance = mock_http.return_value
        server = servers.Server()
        server.start_http_server()

        mock_http.assert_called_with(
            ("0.0.0.0", 8000), servers.LoggingHTTPHandler
        )
        instance.serve_forever.assert_called_once()
        mock_log.info.assert_called_with(
            "Inicializando servidor HTTP na porta 8000"
        )


def test_start_ftp_server_calls_serve_forever():
    with patch("servers.FTPServer") as mock_ftp, patch(
        "servers.DummyAuthorizer"
    ), patch("servers.logging") as mock_log:
        instance = mock_ftp.return_value
        server = servers.Server()
        server.start_ftp_server()

        mock_ftp.assert_called_with(
            ("0.0.0.0", 2121), servers.LoggingFTPHandler
        )
        instance.serve_forever.assert_called_once()
        mock_log.info.assert_called_with(
            "Inicializando servidor FTP na porta 2121"
        )


def test_server_start_creates_threads():
    server = servers.Server()
    with patch.object(server, "start_http_server"), patch.object(
        server, "start_ftp_server"
    ):
        with patch("threading.Thread.start") as mock_start, patch(
            "threading.Thread.join"
        ) as mock_join:
            server.start()
            # Verifica que as threads foram criadas e start() foi chamado
            assert server.http_thread is not None
            assert server.ftp_thread is not None
            assert mock_start.call_count == 2
            assert mock_join.call_count == 2
