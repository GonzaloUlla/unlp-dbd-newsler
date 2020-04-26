# unlp-dbd-newsler

Newsler - News crawler from Web Sites and Twitter - Database Design

Diseño de Bases de Datos (DBD) - MS in Software Engineering 2019/2020 - UNLP

## Table of Contents

- [unlp-dbd-newsler](#unlp-dbd-newsler)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
    - [Dependencies](#dependencies)
    - [Configuration](#configuration)
  - [Getting Started](#getting-started)
    - [Running everything with Docker](#running-everything-with-docker)
    - [Running only news-crawler](#running-only-news-crawler)
    - [Running only twitter-crawler](#running-only-twitter-crawler)
  - [Conventions](#conventions)
    - [Style Guide](#style-guide)
    - [Branching Model](#branching-model)
    - [Contributing](#contributing)
  - [Authors](#authors)

## Prerequisites

### Dependencies

- Python 3.8
  - How to install latest stable release [here](https://tecadmin.net/install-python-3-8-ubuntu/)
- Scrapy 2.0.1, Tweepy 3.8.0 and JsonLines 1.2.0
  - `pip install -r requirements.txt`

### Configuration

- Create a **.env** file inside `twitter-crawler` with the following keys

```bash
CONSUMER_KEY=<KEY-WITHOUT-QUOTES>
CONSUMER_SECRET=<KEY-WITHOUT-QUOTES>
ACCESS_TOKEN=<KEY-WITHOUT-QUOTES>
ACCESS_TOKEN_SECRET=<KEY-WITHOUT-QUOTES>
LOGGING_LEVEL=<DEBUG|INFO|WARN|ERROR>
```

- If you are not using Docker, remember to export the previous keys

```bash
export CONSUMER_KEY=<KEY-WITHOUT-QUOTES>
export CONSUMER_SECRET=<KEY-WITHOUT-QUOTES>
export ACCESS_TOKEN=<KEY-WITHOUT-QUOTES>
export ACCESS_TOKEN_SECRET=<KEY-WITHOUT-QUOTES>
export LOGGING_LEVEL=<DEBUG|INFO|WARN|ERROR>
```

## Getting Started

### Running everything with Docker

```bash
# If you are using a VM or Elasticsearch exits with code 78, run this with root:
# sysctl -w vm.max_map_count=262144

# Single-node Elasticsearch
docker-compose up -d

# Multi-node Elasticsearch
docker-compose -f docker-compose-ha.yml up -d
```

### Running only news-crawler

- Run all Spiders (WIP: Template Method version)

```bash
cd news-crawler
python3.8 spiders/websites.py
```

### Running only twitter-crawler

- Run polling scrapers

```bash
cd twitter-crawler
python3.8 -m scrapers.polling scrapers/polling.py
```

- Run streaming scrapers

```bash
cd twitter-crawler
python3.8 -m scrapers.streaming scrapers/streaming.py
```

## Conventions

### Style Guide

- [PEP8](https://www.python.org/dev/peps/pep-0008/)

### Branching Model

Pushing to **feature** branches and then opening a Pull Request to **master**. Refer to [CONTRIBUTING.md](https://github.com/GonzaloUlla/unlp-dbd-newsler/blob/master/CONTRIBUTING.md)

### Contributing

To contribute to the project, get in touch with one of the [Authors](#Authors).

Check our [Contributing](https://github.com/GonzaloUlla/unlp-dbd-newsler/blob/master/CONTRIBUTING.md) and [Code of Conduct](https://github.com/GonzaloUlla/unlp-dbd-newsler/blob/master/CODE_OF_CONDUCT.md) documents.

## Authors

- **DE LA VEGA, Matías** - _delaVega.Matias@gmail.com_

- **FRÍAS, Pablo** - _pablosfrias@gmail.com_

- **RÍOS, Julieta** - _julirios299@gmail.com_

- **ULLA, Gonzalo** - _gonzaulla@gmail.com_
