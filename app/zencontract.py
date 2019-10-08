from pathlib import Path

from zenroom.zenroom import zencode_exec, ZenroomException

from app.config.config import BaseConfig


class CONTRACTS:
    GENERATE_KEYPAIR = "issuer_keygen.zen"
    PUBLIC_VERIFY = "publish_verifier.zen"
    BLIND_SIGN = "issuer_sign.zen"
    CITIZEN_KEYGEN = "credential_keygen.zen"
    CITIZEN_REQ_BLIND_SIG = "create_request.zen"
    AGGREGATE_CREDENTIAL = "aggregate_signature.zen"
    PROVE_CREDENTIAL = "create_proof.zen"
    VERIFY_CREDENTIAL = "verify_proof.zen"
    CREATE_PETITION = "create_petition.zen"
    APPROVE_PETITION = "approve_petition.zen"
    SIGN_PETITION = "sign_petition.zen"
    INCREMENT_PETITION = "aggregate_petition_signature.zen"
    TALLY_PETITION = "tally_petition.zen"
    COUNT_PETITION = "count_petition.zen"


config = BaseConfig()
log = config.logger


class ZenContract(object):
    def __init__(self, name, placeholder={}):
        self.name = name
        self._keys = None
        self._data = None
        self._error = None
        self.placeholder = placeholder
        self.zencode = self.get_contract()

    def get_contract(self):
        contracts_dir = Path(config.get("contracts_path"))
        contract = contracts_dir.joinpath(self.name).read_text()
        for k, v in self.placeholder.items():
            contract = contract.replace(f"'{k}'", f"'{v}'")
        return str(contract)

    def execute(self):
        if config.getboolean("debug"):  # pragma: no cover
            log.debug("+" * 50)
            log.debug("EXECUTING %s" % self.name)
            log.debug("+" * 50)
            log.debug("DATA: %s" % self._data)
            log.debug("KEYS: %s" % self._keys)
            log.debug("CODE: \n%s" % self.zencode)
        try:
            result = zencode_exec(
                script=self.zencode, keys=self._keys, data=self._data
            )
        except ZenroomException:
            log.exception("Zenroom contract exception", exc_info=True)
        return result.stdout

    def keys(self, keys=None):
        if keys:
            self._keys = keys
        return self._keys

    def data(self, data=None):
        if data:
            self._data = data
        return self._data
