# unlp-dbd-newsler

Newsler - News crawler from Web Sites and Twitter - Database Design

Diseño de Bases de Datos (DBD) - MS in Software Engineering 2019/2020 - UNLP

## Table of Contents

- [unlp-dbd-newsler](#unlp-dbd-newsler)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
  - [Conventions](#conventions)
    - [Style Guide](#style-guide)
    - [Branching Model](#branching-model)
    - [Contributing](#contributing)
  - [Authors](#authors)

## Prerequisites

- Python 3.8
  - How to install latest stable release [here](https://tecadmin.net/install-python-3-8-ubuntu/)
- Scrapy 2.0.1
  - `pip install -r requirements.txt`

## Getting Started

### Running news-crawler

- Running one Spider

```bash
# Check scrapy.org
cd scrapy_prototype/spiders
scrapy runspider the_guardian_spider.py -o the_guardian_spider.json 2>&1 | tee -a the_guardian_spider.log
```

- Running with Docker

```bash
# If you are using a VM or Elasticsearch exits with code 78, run this with root:
#sysctl -w vm.max_map_count=262144

# Single-node Elasticsearch
docker-compose up -d

# Multi-node Elasticsearch
docker-compose -f docker-compose-ha.yml up -d
```

- Run all Spiders (WIP: Template Method version)

```bash
python3.8 news-crawler/spiders/websites.py
```

### Running twitter-crawler

- Twitter-crawler prerequisites

Create a **.env** file inside `twitter-crawler` with the following keys.

```bash
CONSUMER_KEY=
CONSUMER_SECRET=
ACCESS_TOKEN=
ACCESS_TOKEN_SECRET=
```

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
