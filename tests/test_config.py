import os

import pytest

from app.config.config import CONFIG_FILE_ENV, BaseConfig


@pytest.mark.xfail(raises=RuntimeError)
def test_wrong_config():
    os.environ[CONFIG_FILE_ENV] = "/fake/file"
    config = BaseConfig()
    assert config.get("uid")
