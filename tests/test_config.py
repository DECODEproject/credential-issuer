import os
from logging import Logger

import pytest

from app.config.config import CONFIG_FILE_ENV, BaseConfig


def test_config_base_logger():
    config = BaseConfig()
    assert type(config.logger) is Logger


def test_config_get():
    config = BaseConfig()
    assert config.get("uid") == "issuer_identifier"


def test_config_getint():
    config = BaseConfig()
    assert config.getint("ACCESS_TOKEN_EXPIRE_MINUTES") == 30
    assert type(config.getint("ACCESS_TOKEN_EXPIRE_MINUTES")) is int


def test_config_getboolean():
    config = BaseConfig()
    assert config.getboolean("debug") is True
    assert type(config.getboolean("debug")) is bool


@pytest.mark.xfail(raises=RuntimeError)
def test_wrong_config():
    os.environ[CONFIG_FILE_ENV] = "/fake/file"
    config = BaseConfig()
    assert config.get("uid")
