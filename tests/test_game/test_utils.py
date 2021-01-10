import pytest

from game.errors import ConfigError
from game.utils import check_os_config


def test_check_os_config_env_vars(monkeypatch):
    host = 'localhost'
    port = '12345'
    monkeypatch.setenv('HOST', host)
    monkeypatch.setenv('PORT', port)

    assert check_os_config('HOST') == host
    assert check_os_config('PORT') == port


def test_check_os_config_missing_host(monkeypatch):
    with pytest.raises(ConfigError) as err:
        check_os_config('HOST')

    err.match('Environment variable HOST not set or not passed to Server.')


def test_check_os_config_missing_port(monkeypatch):
    with pytest.raises(ConfigError) as err:
        check_os_config('PORT')

    err.match('Environment variable PORT not set or not passed to Server.')


@pytest.mark.parametrize('test_input, expected_output', [
    (('HOST', 'localhost'), 'localhost'),
    (('HOST', '192.168.1.1'), '192.168.1.1'),
    (('HOST', '192.168.1.1'), '192.168.1.1'),
    (('PORT', 12345), 12345),
    (('PORT', '12345'), '12345'),
    ])
def test_check_os_config_pass_config(test_input, expected_output):
    assert check_os_config(*test_input) == expected_output
