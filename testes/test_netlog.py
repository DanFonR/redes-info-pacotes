from pathlib import Path
from scapy.layers.inet import IP, TCP
from unittest.mock import MagicMock, patch

import pytest

from netlog import NetLogger


# Fixture para NetLogger com CSV temporário
@pytest.fixture
def netlogger(tmp_path: Path) -> NetLogger:
    """
    Cria instância do NetLogger com CSV temporário.
    """
    csv_file: Path = tmp_path / "test.csv"
    return NetLogger(str(csv_file))


def fake_packet(
    src="127.0.0.1",
    dst="127.0.0.2",
    proto=6,
    size=100,
    sport=12345,
    dport=8000,
) -> MagicMock:
    """
    Cria um pacote falso com IP e TCP, adequado para passar pelos filtros de NetLogger.
    """
    ip = MagicMock()
    ip.src = src
    ip.dst = dst
    ip.proto = proto

    tcp = MagicMock()
    tcp.sport = sport
    tcp.dport = dport

    pkt = MagicMock()
    # suporta 'IP in pkt' e 'TCP in pkt'
    pkt.__contains__.side_effect = lambda x: x in (IP, TCP)
    pkt.__getitem__.side_effect = lambda x: ip if x == IP else tcp
    pkt.__len__.return_value = size

    return pkt


def test_processa_pacotes_single_logging(netlogger: NetLogger) -> None:
    """
    Verifica CSV e log com captura de 1 pacote.
    """
    pkt = fake_packet(dport=8000)  # HTTP port
    with patch("netlog.sniff", return_value=[pkt]), patch("netlog.logging") as mock_log:
        netlogger.conexoes = {"127.0.0.1", "127.0.0.2"}
        netlogger.processa_pacotes(timeout=1)

        mock_log.info.assert_called_with("Iteração 1 concluída")

        with open(netlogger.csv_path) as f:
            lines = f.readlines()
        assert len(lines) == 3  # header + 2 linhas (src/dst)


def test_processa_pacotes_multiple_logging(netlogger: NetLogger) -> None:
    """
    Verifica CSV e log com captura de múltiplos pacotes.
    """
    pkt1 = fake_packet(
        src="127.1.1.1", dst="127.2.2.2", proto=6, sport=5000, dport=8000
    )
    pkt2 = fake_packet(
        src="127.3.3.3", dst="127.4.4.4", proto=17, sport=6000, dport=2121
    )  # FTP port

    with (
        patch("netlog.sniff", return_value=[pkt1, pkt2]),
        patch("netlog.logging") as mock_log,
    ):
        netlogger.conexoes = {"127.1.1.1", "127.2.2.2", "127.3.3.3", "127.4.4.4"}
        netlogger.processa_pacotes(timeout=1)

        mock_log.info.assert_called_with("Iteração 1 concluída")

        with open(netlogger.csv_path) as f:
            lines = f.readlines()
        assert len(lines) == 5  # header + 4 linhas (2 pacotes x 2)


def test_run_interruption(monkeypatch, netlogger: NetLogger) -> None:
    """
    Garante que run() respeita interrupção manual.
    """

    netlogger.interrompeu = True

    with (
        patch("netlog.sniff") as mock_sniff,
        patch("netlog.logging") as mock_log,
    ):
        netlogger.run()
        # sniff não deve ser chamado
        mock_sniff.assert_not_called()
        # Logging deve registrar interrupção manual
        mock_log.info.assert_called_with("Execução interrompida manualmente")


def test_run_exception_logging(netlogger: NetLogger) -> None:
    """
    Verifica se exceções em run() são logadas.
    """

    with (
        patch("netlog.sniff", side_effect=Exception("Erro fake")),
        patch("netlog.logging") as mock_log,
    ):
        # Força interrupção só depois do primeiro loop
        def interrompe_apos_primeiro_loop(*args, **kwargs):
            netlogger.interrompeu = True
            raise Exception("Erro fake")

        with patch("netlog.sniff", side_effect=interrompe_apos_primeiro_loop):
            netlogger.run()

        assert mock_log.warning.called
