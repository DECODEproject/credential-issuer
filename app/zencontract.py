from pathlib import Path

from zenroom import zenroom

from app.config.config import BaseConfig


class CONTRACTS:
    GENERATE_KEYPAIR = "03-CREDENTIAL_ISSUER-keygen.zencode"
    PUBLIC_VERIFY = "04-CREDENTIAL_ISSUER-publish-verifier.zencode"
    BLIND_SIGN = "05-CREDENTIAL_ISSUER-credential-sign.zencode"
    CITIZEN_KEYGEN = "01-CITIZEN-credential-keygen.zencode"
    CITIZEN_REQ_BLIND_SIG = "02-CITIZEN-credential-request.zencode"
    AGGREGATE_CREDENTIAL = "06-CITIZEN-aggregate-credential-signature.zencode"
    PROVE_CREDENTIAL = "07-CITIZEN-prove-credential.zencode"
    VERIFY_CREDENTIAL = "08-VERIFIER-verify-credential.zencode"
    CREATE_PETITION = "09-CITIZEN-create-petition.zencode"
    APPROVE_PETITION = "10-VERIFIER-approve-petition.zencode"
    SIGN_PETITION = "11-CITIZEN-sign-petition.zencode"
    INCREMENT_PETITION = "12-LEDGER-add-signed-petition.zencode"
    TALLY_PETITION = "13-CITIZEN-tally-petition.zencode"
    COUNT_PETITION = "14-CITIZEN-count-petition.zencode"


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
        return contract

    def execute(self):
        if config.getboolean("debug"):  # pragma: no cover
            log.debug("+" * 50)
            log.debug("EXECUTING %s" % self.name)
            log.debug("+" * 50)
            log.debug("DATA: %s" % self._data)
            log.debug("KEYS: %s" % self._keys)
            log.debug("CODE: \n%s" % self.zencode)

        result, errors = zenroom.zencode_exec(
            script=self.zencode, keys=self._keys, data=self._data
        )
        self._error = errors
        return result

    def keys(self, keys=None):
        if keys:
            self._keys = keys
        return self._keys

    def data(self, data=None):
        if data:
            self._data = data
        return self._data

    def errors(self):
        return self._error
