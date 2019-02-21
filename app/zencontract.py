from zenroom import zenroom

from app.config.config import BaseConfig
from app.utils import get_contract


class CONTRACTS:
    GENERATE_KEYPAIR = "03-CREDENTIAL_ISSUER-keypair.zencode"
    PUBLIC_VERIFY = "04-CREDENTIAL_ISSUER-public-verify-keypair.zencode"
    BLIND_SIGN = "05-CREDENTIAL_ISSUER-credential-blind-signature.zencode"
    CITIZEN_KEYGEN = "01-CITIZEN-request-keypair.zencode"
    CITIZEN_REQ_BLIND_SIG = "02-CITIZEN-request-blind-signature.zencode"


config = BaseConfig()
log = config.logger


class ZenContract(object):
    def __init__(self, name):
        self.name = name
        self._keys = None
        self._data = None
        self.zencode = get_contract(self.name)

    def execute(self):
        if config.get("debug"):  # pragma: no cover
            log.debug("+" * 50)
            log.debug("EXECUTING %s" % self.name)
            log.debug("+" * 50)
            log.debug("DATA: %s" % self.data())
            log.debug("KEYS: %s" % self.keys())
            log.debug("CODE: \n%s" % self.zencode.decode())
        return zenroom.execute(self.zencode, keys=self._keys, data=self._data).decode()

    def keys(self, keys=None):
        if keys:
            self._keys = keys.encode()
        return self._keys.decode() if self._keys else None

    def data(self, data=None):
        if data:
            self._data = data.encode()
        return self._data.decode() if self._data else None
