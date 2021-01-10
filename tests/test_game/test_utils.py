import pytest

from game.errors import ConfigError
from game.utils import check_os_config, random_xy, sync_value_with_grid


def test_check_os_config_env_vars(monkeypatch):
    host = 'localhost'
    port = 12345
    monkeypatch.setenv('HOST', host)
    monkeypatch.setenv('PORT', str(port))

    assert isinstance(check_os_config('HOST'), str)
    assert isinstance(check_os_config('PORT'), int)
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


@pytest.mark.parametrize('test_input', [
    {(70, 190), (100, 380), (230, 90), (50, 370), (130, 250),
     (180, 80), (260, 350), (310, 180), (290, 360), (0, 140), (320, 230)},
    {(160, 390), (290, 240), (0, 20), (80, 290), (320, 110)},
    {(320, 380), (260, 100), (160, 260), (240, 280)}
    ])
def test_random_xy(test_input):
    assert random_xy(test_input) in test_input


@pytest.mark.parametrize('test_input, expected_output', [
    (5.4, 10), (0, 0), (10.23451, 10), (212, 210), (15.5, 20), (1, 0),
    (-5, 0), (-7.7, -10), (5, 10)
    ])
def test_sync_value_with_grid(test_input, expected_output):
    assert sync_value_with_grid(test_input) == expected_output
