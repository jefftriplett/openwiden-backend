# openwiden-backend

[![Build Status](https://travis-ci.com/OpenWiden/openwiden-backend.svg?branch=master)](https://travis-ci.com/OpenWiden/openwiden-backend)
[![codecov](https://codecov.io/gh/OpenWiden/openwiden-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/OpenWiden/openwiden-backend)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

OpenWiden - An Open Source Project Search Platform.

# Prerequisites

- [Docker]  

# Local Development

Start the dev server for local development:
```bash
docker-compose up
```
Or using a shortcut via [make]
```bash
make up
```

Run a command inside the docker container:

```bash
docker-compose run --rm web [command]
```
Or using a shortcut via [make]
```bash
make web c="python --version"
```


[make]: https://en.wikipedia.org/wiki/Make_(software)
[docker]: https://docs.docker.com/docker-for-mac/install/