<h1 align="center">
  <br>
        <a href="https://decodeproject.eu/">
                <img src="https://decodeproject.eu/sites/all/themes/marmelo_base/img/logo.svg" width="300" alt="dddc-credential-issuer">
        </a>
  <br>
  DDDC Credential Issuer API
  <br>
</h1>


| Restful API for the Credential issuer of the Digital Democracy and Data Commons pilot project |
:---:
| [![Build Status](https://travis-ci.com/DECODEproject/dddc-credential-issuer.svg?branch=master)](https://travis-ci.com/DECODEproject/dddc-credential-issuer) [![codecov](https://codecov.io/gh/DECODEproject/dddc-credential-issuer/branch/master/graph/badge.svg)](https://codecov.io/gh/DECODEproject/dddc-credential-issuer) [![Dyne.org](https://img.shields.io/badge/%3C%2F%3E%20with%20%E2%9D%A4%20by-Dyne.org-blue.svg)](https://dyne.org) |

<br><br>

Credential issuer API is part of the DDDC.
Digital Democracy and Data Commons is a pilot participatory process oriented to test a new technology to improve the 
digital democracy platform Decidim and to collectively imagine the data politics of the future. This pilot takes place 
in the context of the European project [DECODE (Decentralized Citizen Owned Data Ecosystem)](https://decodeproject.eu) 
that aims to construct legal, technological, and socioeconomic tools that allow citizens to take back control over their
data and [technological sovereignty](https://www.youtube.com/watch?v=RvBRbwBm_nQ). Our effort is that of improving
people's awareness of how their data is processed by algorithms, as well facilitate the work of developers to create along
[privacy by design principles](https://decodeproject.eu/publications/privacy-design-strategies-decode-architecture) 
using algorithms that can be deployed in any situation without any change.


<details>
 <summary><strong>:triangular_flag_on_post: Table of Contents</strong> (click to expand)</summary>

* [Getting started](#rocket_getting-started)
* [Install](#floppy_disk-install)
* [Usage](#video_game-usage)
* [Docker](#whale-docker)
* [API](#honeybee-api)
* [Configuration](#wrench-configuration)
* [Testing](#clipboard-testing)
* [Troubleshooting & debugging](#bug-troubleshooting--debugging)
* [Acknowledgements](#heart_eyes-acknowledgements)
* [Links](#globe_with_meridians-links)
* [Contributing](#busts_in_silhouette-contributing)
* [License](#briefcase-license)
</details>

***
## :rocket: Getting started

> This requires docker to be installed


```bash
git clone --recursive https://github.com/DECODEproject/dddc-credential-issuer.git
cd dddc-credential-issuer
./start.sh
```

This will clone the project and all submodules of the project (**--recursive** is important)
then by lunching the `start.sh` will create a docker container with all the dependencies correctly
configured.

Head your browser to:

**SWAGGER UI**: http://0.0.0.0/docs/

**API**: http://0.0.0.0/ 

for the authentication in the SWAGGER UI over the calls, that need the OAuth2 
and JWT token please use the following credentials:


| username | password |
| :---: | :---: |
| demo | demo |

**NB:** `client_id` and `client_secret` are not mandatory and should be empty

***
## :floppy_disk: Install

To locally run you need to run over a the API project over an [ASGI](https://asgi.readthedocs.io/en/latest/) server 
like [uvicorn](https://www.uvicorn.org/).

Assuming you are already cloned the project as described on [Getting started](#rocket_getting-started) with the 
submodules and already `cd` into your project directory `dddc-credential-issuer` you need the following steps

1. create a `virtualenv`
1. activate the virtualenv
1. upgrade the pip
1. install dependencies
1. install the ASGI serve
1. run locally the API

```bash
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install uvicorn
uvicorn app.main:api --debug
```


***
## :video_game: Usage

This API server is meant for the Credential Issuing of the DDDC Project part of the 

<img width="800" src="https://github.com/DECODEproject/decidim-pilot-infrastructure/raw/master/docs/infrastructure-overview.png" ></img>

This will handle both the credential issuing with Coconut (for the wallet) and the interaction with the DDDC Site as 
described [here](REQUIREMENTS.md)

***
## :whale: Docker

```bash
docker build -t dddc-credential-issuer .
docker run --rm -p 80:80 -e APP_MODULE="app.main:api" -e LOG_LEVEL="debug" -it dddc-credential-issuer
```

All the options are documented on [here](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#advanced-usage)

***
## :honeybee: API

All the parameters and format of the input are documented on the swagger, below you'll find a quick description of each
endpoint 


#### /token
This returns a valid JWT to be used over OAuth2 covered calls in the `Bearer` header

#### /authorizable_attribute
Creates an Authorizable Attibute as defined on [here](REQUIREMENTS.md)
it contains an `authorizable_attribute_id` and a `authorizable_attribute_info` in form of a list of objects 
each one with a key and values

This will create the rules to allow people to obtain a credential. Each credential
will have it's own keypair (in form of a Credential Issuer Keypair, Coconut flow 03)
and the public `verification_key` will be printed as a result

#### /authorizable_attribute/{authorizable_attribute_id}

This allows to retrieve the Authorizable Attibute by the `authorizable_attribute_id`

This will contain the ruleset and the verification_key

#### /credential

This will check that the information provided are a correct subset of the information of the Authorizable Attribute
and if they are correct it will sign (add a sigma_tilde) and release a credential
for the user (coconut flow 05)

#### /uid

Gives back the Credential Issuer `ci_unique_id` a string that  identifies the credential issue instance.

***
## :wrench: Configuration

All the configuration should be available under an .ini file.
By default the configuration file is [config.ini](app/config.ini)

### User defined config.ini
Define a environment variable **DDDC_CREDENTIAL_ISSUER_CONFIGFILE** with the absolute path of the file like:

```bash
export DDDC_CREDENTIAL_ISSUER_CONFIGFILE=/srv/some/secure/place/production.ini
```

You are **encouraged to do this** and edit the config file with your real data.


### Variables

| name | description | values | 
| --- | --- | --- |
| **debug** | This **should be off** in production add some verbose logging | `true` or `false` |
| **uid** | The `ci_unique_id`. A string that identifies the credential issue instance | `string` |
| **keypair** | The secret keypair path of the Credential Issuer, if the file does not exists, it is created the first a request is run | `file absolute path` |
| **contracts_path** | The path of the Zencode smart contracts for now a submodule of [dddc-pilot-contracts](https://github.com/DECODEproject/dddc-pilot-contracts) | `directory absolute path` |
| **ALGORITHM** | The algorithm used for the `JWT` generation | [available algorithms](https://pyjwt.readthedocs.io/en/latest/algorithms.html?highlight=algorithm#digital-signature-algorithms) |
| **ACCESS_TOKEN_EXPIRE_MINUTES** | Minutes of validity of the JWT tokens | `int` |
| **SQLALCHEMY_DATABASE_URI** | The url of your relational database (sqlite is tested by now) | [SQLAlchemy Database URL](https://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls) | 


***
## :clipboard: Testing

```bash
python3 setup.py test
```

***
## :bug: Troubleshooting & debugging

To run the `credential-issuer` in debug mode, please run it in local and activate `--debug` when you launch the ASGI
uvicorn server. 

Set the `LOG_LEVEL="debug"` ENVIRONMENT VARIABLE that is used by `uvicorn` and `starlette`.

Configure your [`config.ini`](app/config.ini) and set the 

```ini
debug = true
```


***
## :heart_eyes: Acknowledgements

Copyright :copyright: 2019 by [Dyne.org](https://www.dyne.org) foundation, Amsterdam

Designed, written and maintained by Puria Nafisi Azizi.

<img src="https://zenroom.dyne.org/img/ec_logo.png" class="pic" alt="Project funded by the European Commission">

This project is receiving funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement nr. 732546 (DECODE).


***
## :globe_with_meridians: Links

https://decodeproject.eu/

https://dyne.org/

https://zenroom.dyne.org/

https://dddc.decodeproject.eu/


***
## :busts_in_silhouette: Contributing

Please first take a look at the [Dyne.org - Contributor License Agreement](CONTRIBUTING.md) then

1.  :twisted_rightwards_arrows: [FORK IT](https://github.com/puria/README/fork)
2.  Create your feature branch `git checkout -b feature/branch`
3.  Commit your changes `git commit -am 'Add some fooBar'`
4.  Push to the branch `git push origin feature/branch`
5.  Create a new Pull Request
6.  :pray: Thank you


***
## :briefcase: License

	DDDC Credential Issuer API
    Copyright (c) 2019 Dyne.org foundation, Amsterdam

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.

