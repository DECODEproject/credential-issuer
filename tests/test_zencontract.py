from app.zencontract import ZenContract, CONTRACTS


def test_zecontract():
    smart_contract = ZenContract(CONTRACTS.GENERATE_KEYPAIR)
    assert smart_contract
    assert not smart_contract.data()
    assert not smart_contract.keys()


def test_data():
    smart_contract = ZenContract(CONTRACTS.GENERATE_KEYPAIR)
    smart_contract.data("test")

    assert smart_contract.data() == "test"


def test_keys():
    smart_contract = ZenContract(CONTRACTS.GENERATE_KEYPAIR)
    smart_contract.keys("test")

    assert smart_contract.keys() == "test"


def test_execute():
    smart_contract = ZenContract(CONTRACTS.GENERATE_KEYPAIR)
    result = smart_contract.execute()
    assert result
    expected = ["encoding", "x", "zenroom", "sign", "schema", "curve"]
    for _ in expected:
        assert _ in result
