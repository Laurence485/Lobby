import pytest

from network.network import Network


@pytest.fixture
def mock_os_config(monkeypatch):
    host = 'localhost'
    port = 12345
    monkeypatch.setenv('HOST', host)
    monkeypatch.setenv('PORT', str(port))

    return host, port


@pytest.fixture
def mock_server():
    pass


def test_init(mock_os_config, mock_server):
    net = Network()
    assert net.addr == mock_os_config
    assert net.data
