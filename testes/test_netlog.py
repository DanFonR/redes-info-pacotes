from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from scapy.layers.inet import IP

from netlog import NetLogger


# Fixture para NetLogger com CSV temporário
@pytest.fixture
def netlogger(tmp_path: Path) -> NetLogger:
    csv_file: Path = tmp_path / "test.csv"
    return NetLogger(str(csv_file))


def fake_packet(src="127.0.0.1", dst="127.0.0.2", proto=6, size=100) -> MagicMock:
    """
    Cria um pacote falso com IP e tamanho definidos.
    """

    ip: MagicMock = MagicMock()
    ip.src = src
    ip.dst = dst
    ip.proto = proto

    pkt: MagicMock = MagicMock()
    pkt.__contains__.side_effect = lambda x: x == IP
    pkt.__getitem__.side_effect = lambda x: ip
    pkt.__len__.return_value = size

    return pkt


def test_processa_pacotes_single_logging(netlogger: NetLogger) -> None:
    """
    Pacote único gera CSV e log corretos.
    """

    pkt: MagicMock = fake_packet()
    with (
        patch("netlog.sniff", return_value=[pkt]),
        patch("netlog.logging") as mock_log,
    ):
        netlogger.conexoes = {"127.0.0.1", "127.0.0.2"}
        netlogger.processa_pacotes(timeout=1)

        # Logging
        mock_log.info.assert_called_with("Iteração 1 concluída")

        # CSV: header + 2 linhas (src/dst)
        with open(netlogger.csv_path) as f:
            lines = f.readlines()
        assert len(lines) == 3


def test_processa_pacotes_multiple_logging(netlogger: NetLogger) -> None:
    """
    Múltiplos pacotes geram CSV e log corretos.
    """

    pkt1: MagicMock
    pkt2: MagicMock
    pkt1 = fake_packet(src="127.1.1.1", dst="127.2.2.2", proto=6, size=50)
    pkt2 = fake_packet(src="127.3.3.3", dst="127.4.4.4", proto=17, size=70)

    with (
        patch("netlog.sniff", return_value=[pkt1, pkt2]),
        patch("netlog.logging") as mock_log,
    ):
        netlogger.conexoes = {"127.1.1.1", "127.2.2.2", "127.3.3.3", "127.4.4.4"}
        netlogger.processa_pacotes(timeout=1)

        mock_log.info.assert_called_with("Iteração 1 concluída")

        # CSV: header + 4 linhas (2 pacotes x 2)
        with open(netlogger.csv_path) as f:
            lines = f.readlines()
        assert len(lines) == 5


def test_run_interruption(monkeypatch, netlogger: NetLogger) -> None:
    """
    Testa run() com interrupção imediata (interrompeu=True).
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
