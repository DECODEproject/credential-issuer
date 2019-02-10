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

```bash
./start.sh
```
> This requires docker to be installed

Head your browser to:

**SWAGGER UI**: http://127.0.0.1/docs/

**API**: http://127.0.0.1/ 


***
## :floppy_disk: Install
```pip install -e .```

***
## :video_game: Usage

To start using {project_name} just (fill with real documentation)

***
## :whale: Docker

```bash
docker build -t dddc-credential-issuer .
docker run --rm -p 80:80 -e APP_MODULE="app.main:api" -e LOG_LEVEL="debug" -it dddc-credential-issuer
```

All the options are documented on [here](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#advanced-usage)

***
## :honeybee: API

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


***
## :clipboard: Testing

```bash
python3 setup.py test
```

***
## :bug: Troubleshooting & debugging


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

    Copyright (c) 2019 Dyne.org foundation, Amsterdam

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

