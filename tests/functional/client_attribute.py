import os
import sys

"""

Script to set up a test authorizable_attribute

To be run by DDDC Admin.

Please set your env variables to set username, password and API Credential issuer URL.


First parameter passed to the script is the authorizable_attribute_id

Author: Oleguer Sagarra <ula@dribia.com> Dribia Data Research S.L.

"""
# confs
exhaust_credential = False  # exhaust credential (consume once)
create_credential = True  # create credential (create credentials)
# imports and set-up
print("### Importing modules")

try:
    import requests
except ImportError:
    print("\tNo requests found, will download it using pip")
    # donwload
    os.system("pip install requests")

try:
    aa_id = str(sys.argv[1])
except IndexError:
    aa_id = "testing_aa_id"
    print("\t Could not load a user defined aa_id, using {}".format(aa_id))
aa_id2 = aa_id + "_reissuable"
# defaults
API_URL_default = "http://0.0.0.0/"
API_USERNAME_default = "demo"
API_PASS_default = "demo"
ENV_VARS = ["API_URL", "API_USERNAME", "API_PASS"]
ENV_VARS_DICT_DEFAULT = {
    "API_URL": API_URL_default,
    "API_USERNAME": API_USERNAME_default,
    "API_PASS": API_PASS_default,
}
if create_credential:
    print(
        "#### - #### - #####\n We will create two authorizable attributes with ids {},{}, lets go!".format(
            aa_id, aa_id2
        )
    )
# STEP 0: COnfig params
print("### Solving parameters")
ENV_VARS_DICT = {}
for var_name in ENV_VARS:
    var = os.environ.get("CIAPI_URL", None)
    if var is None:
        print(
            "\tNo {} env variable found, using default {}".format(
                var_name, ENV_VARS_DICT_DEFAULT[var_name]
            )
        )
    ENV_VARS_DICT[var_name] = ENV_VARS_DICT_DEFAULT[var_name]
# STEP 1: GEt token
print("### Getting token")
# curl -X POST "https://petitions.decodeproject.eu/token" -H  "accept: application/json" -H  "Content-Type: application/x-www-form-urlencoded" -d "grant_type=&username=us&password=pass"
res = requests.post(
    ENV_VARS_DICT["API_URL"] + "token",
    data={
        "username": ENV_VARS_DICT["API_USERNAME"],
        "password": ENV_VARS_DICT["API_PASS"],
    },
)
if res.ok:
    print("\tAll good, got this token as result: {}".format(res.json()))
    token_data = res.json()
else:
    print("\tCalls not getting back, got this error: {}".format(res.json()))
    sys.exit()
# STEP 2: Set up AA_id
if create_credential:
    print("### Setting up authorizable_attribute")
    # curl -X POST "http://0.0.0.0/authorizable_attribute" -H  "accept: application/json" -H  "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImRlbW8iLCJleHAiOjE1NTE4OTAzODksInN1YiI6ImFjY2VzcyJ9.yJ91u2VsG2MuowdlpuKTtmwEEB9fEZt7TqCZpsgJZxY" -H  "Content-Type: application/json" -d "{\"authorizable_attribute_id\":\"Authorizable Attribute b78F4efD57\",\"authorizable_attribute_info\":[{\"name\":\"email\",\"type\":\"str\",\"value_set\":[\"andres@example.com\",\"jordi@example.com\",\"pablo@example.com\"]},{\"name\":\"zip_code\",\"type\":\"int\",\"value_set\":[\"08001\",\"08002\",\"08003\",\"08004\",\"08005\",\"08006\"]}],\"reissuable\":false}"
    data_aa = {
        "authorizable_attribute_id": aa_id,
        "authorizable_attribute_info": [
            {"name": "email", "type": "str", "value_set": ["test@test.com"]},
            {"name": "random_number", "type": "int", "value_set": [1234]},
        ],
        "reissuable": False,
    }
    data_aa2 = {
        "authorizable_attribute_id": aa_id2,
        "authorizable_attribute_info": [
            {"name": "email", "type": "str", "value_set": ["test@test.com"]},
            {"name": "random_number", "type": "int", "value_set": [1234]},
        ],
        "reissuable": True,
    }
    headers = {"Authorization": "Bearer " + token_data["access_token"]}
    res = requests.post(
        ENV_VARS_DICT["API_URL"] + "authorizable_attribute",
        json=data_aa,
        headers=headers,
    )
    if res.ok:
        print("\tAll good, got this result: {}".format(res.json()))
        token_data = res.json()
    else:
        print("\tCalls not getting back, got this error: {}".format(res.json()))
        sys.exit()
    res = requests.post(
        ENV_VARS_DICT["API_URL"] + "authorizable_attribute",
        json=data_aa2,
        headers=headers,
    )
    if res.ok:
        print("\tAll good, got this result: {}".format(res.json()))
        token_data = res.json()
    else:
        print("\tCalls not getting back, got this error: {}".format(res.json()))
        sys.exit()
# STEP 3: Get AA_id info
# curl -X GET "http://0.0.0.0/authorizable_attribute/testing_aa_id" -H  "accept: application/json"
print("### Testing aa_id public endpoing info")
res = requests.get(ENV_VARS_DICT["API_URL"] + "authorizable_attribute/{}".format(aa_id))
if res.ok:
    print("\tAll good, got this result: {}".format(res.json()))
    token_data = res.json()
else:
    print("\tCalls not getting back, got this error: {}".format(res.json()))
    sys.exit()
res = requests.get(
    ENV_VARS_DICT["API_URL"] + "authorizable_attribute/{}".format(aa_id2)
)
if res.ok:
    print("\tAll good, got this result: {}".format(res.json()))
    token_data = res.json()
else:
    print("\tCalls not getting back, got this error: {}".format(res.json()))
    sys.exit()
# STEP 4: Testing
# curl -X POST "http://0.0.0.0/credential" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"authorizable_attribute_id\":\"Authorizable Attribute Unique Identifier\",\"blind_sign_request\":{\"request\":{\"pi_s\":{\"c\":\"9fbe906553d2d15959094a42e3863f71f90634a15172d30cf5d5cda555836c1a\",\"rk\":\"0cff3b2b8b9e28c63f4902303e4d6ba2c6aac096543098b87ff8fa817be22d61\",\"rm\":\"2698c1e293341ca1d28782a34ef74814249b516431aab963fcb31c19a22f41a0\",\"rr\":\"32c0c70c0f6a65b58ab8f23742e695743c4e3672f1ca4c92fd30545aab4e5b45\"},\"zenroom\":\"0.8.1\",\"schema\":\"lambda\",\"c\":{\"a\":\"040b7c7b31f9c81daf812d87999a9f53e5a2e6c9b1a2a3df42db155066d1c22674acc579798d6d544427b23dd77b379b9e3d4556806f9b2bdd940aba61495f9d392011a639f8d75f1f0e68906f0e1a0d61eda3a2a621e4f173b35a6d00a36dd51d\",\"b\":\"040acd0a9a4b39409c17ea2cbf73354c9f6bb410e126c25865003dcc356bcec31a81c8696e6dbe4011962f98d316f475a01d76d8b95ddd99dc97ef67119f82ccd6bd5711e5c63af48414a945604d620ac4dbf357cd2b250fc787e98ac754b66805\"},\"public\":\"0428f6fd3e9cb1b2a95acce09cc928097f8fe64802b30511d3b18e5fa0f1c50a902c0090b74942070f0fe5e2b84124590b0a45f37507a33ead6cd2f3650f606aea28dbe3506cd0011bddf7657de5d0211582803ea91e67103310d2f2b5c97509d3\",\"cm\":\"043a0ddff5a122cd75a4bda44bd220b13d0d05d2b2e751d02a30b92ca148fd5e56fdf7530bf8c0f1071dab4ccb504b49f522f54047cd15fc4b3a5b34a42c702a8e6e4d396d3e60eb88f309530389c903f1d9f0354f44b1de4d4dccdb28705e677f\",\"encoding\":\"hex\",\"curve\":\"bls383\"}},\"values\":[{\"name\":\"zip_code\",\"value\":\"08001\"},{\"name\":\"email\",\"value\":\"pablo@example.com\"}]}"
data_cred = {
    "authorizable_attribute_id": aa_id,
    "blind_sign_request": {
        "request": {
            "pi_s": {
                "c": "9fbe906553d2d15959094a42e3863f71f90634a15172d30cf5d5cda555836c1a",
                "rk": "0cff3b2b8b9e28c63f4902303e4d6ba2c6aac096543098b87ff8fa817be22d61",
                "rm": "2698c1e293341ca1d28782a34ef74814249b516431aab963fcb31c19a22f41a0",
                "rr": "32c0c70c0f6a65b58ab8f23742e695743c4e3672f1ca4c92fd30545aab4e5b45",
            },
            "zenroom": "0.8.1",
            "schema": "lambda",
            "c": {
                "a": "040b7c7b31f9c81daf812d87999a9f53e5a2e6c9b1a2a3df42db155066d1c22674acc579798d6d544427b23dd77b379b9e3d4556806f9b2bdd940aba61495f9d392011a639f8d75f1f0e68906f0e1a0d61eda3a2a621e4f173b35a6d00a36dd51d",
                "b": "040acd0a9a4b39409c17ea2cbf73354c9f6bb410e126c25865003dcc356bcec31a81c8696e6dbe4011962f98d316f475a01d76d8b95ddd99dc97ef67119f82ccd6bd5711e5c63af48414a945604d620ac4dbf357cd2b250fc787e98ac754b66805",
            },
            "public": "0428f6fd3e9cb1b2a95acce09cc928097f8fe64802b30511d3b18e5fa0f1c50a902c0090b74942070f0fe5e2b84124590b0a45f37507a33ead6cd2f3650f606aea28dbe3506cd0011bddf7657de5d0211582803ea91e67103310d2f2b5c97509d3",
            "cm": "043a0ddff5a122cd75a4bda44bd220b13d0d05d2b2e751d02a30b92ca148fd5e56fdf7530bf8c0f1071dab4ccb504b49f522f54047cd15fc4b3a5b34a42c702a8e6e4d396d3e60eb88f309530389c903f1d9f0354f44b1de4d4dccdb28705e677f",
            "encoding": "hex",
            "curve": "bls383",
        }
    },
    "values": [
        {"name": "random_number", "value": 1234},
        {"name": "email", "value": "test@test.com"},
    ],
}
data_cred2 = data_cred.copy()
data_cred2["authorizable_attribute_id"] = aa_id2
print("### Testing credential access (right)")
if exhaust_credential:
    res = requests.post(ENV_VARS_DICT["API_URL"] + "credential", json=data_cred)
    if res.ok:
        print("\tAll good, got this result: {}".format(res.json()))
        token_data = res.json()
    else:
        print("\tCalls not getting back, got this error: {}".format(res.json()))
        sys.exit()
res = requests.post(ENV_VARS_DICT["API_URL"] + "credential", json=data_cred2)
if res.ok:
    print("\tAll good, got this result: {}".format(res.json()))
    token_data = res.json()
else:
    print("\tCalls not getting back, got this error: {}".format(res.json()))
    sys.exit()

if exhaust_credential:
    print("### Testing credential access (double credential issuing)")
    res = requests.post(ENV_VARS_DICT["API_URL"] + "credential", json=data_cred)
    if not res.ok:
        mess = res.json()["detail"]
        print("\tAll good, credential denied with message: {}".format(res.json()))
    else:
        print("\t Credential should be denied, check API")
        sys.exit()

res = requests.post(ENV_VARS_DICT["API_URL"] + "credential", json=data_cred2)
if not res.ok:
    print("\t Credential should not be denied, check API error {}".format(res.json()))
    sys.exit()

print("### Testing credential access (wrong value on info-set)")
vals = data_cred["values"]
for e in vals:
    if e["name"] == "email":
        e["value"] = "wrongtest@test.com"
data_cred["values"] = vals
res = requests.post(ENV_VARS_DICT["API_URL"] + "credential", json=data_cred)
if not res.ok:
    mess = res.json()["detail"]
    print("\tAll good, credential denied with message: {}".format(res.json()))
else:
    print("\t Credential should be denied, check API")
    sys.exit()
print("### Testing credential access (wrong aa_id)")
data_cred["authorizable_attribute_id"] = "wrong_id"
res = requests.post(ENV_VARS_DICT["API_URL"] + "credential", json=data_cred)
if not res.ok:
    mess = res.json()["detail"]
    print("\tAll good, credential denied with message: {}".format(res.json()))
else:
    print("\t Credential should be denied, check API")
    sys.exit()
