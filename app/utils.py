from pathlib import Path

from app.config.config import BaseConfig

config = BaseConfig()
log = config.logger
CONTRACTS_DIR = Path(config.get("contracts_path"))


def get_contract(name):
    return CONTRACTS_DIR.joinpath(name).read_text().encode()
