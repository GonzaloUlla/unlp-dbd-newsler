# unlp-dbd-newsler

Newsler - News crawler from Web Sites and Twitter - Database Design

Diseño de Bases de Datos (DBD) - MS in Software Engineering 2019/2020 - UNLP

### Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting Started](#getting-started)
3. [Conventions](#conventions)
4. [Authors](#authors)

## Prerequisites

* Python 3.8
  * How to install latest stable release [here](https://tecadmin.net/install-python-3-8-ubuntu/)
* Scrapy 2.0.1
  * `pip install -r requirements.txt`

## Getting Started

* Running Scrapy

```bash
# Check scrapy.org
cd scrapy_prototype
scrapy runspider the_guardian_spider.py -o the_guardian_spider.json 2>&1 | tee -a the_guardian_spider.log
```

* Starting Elasticsearch and Kibana
```bash
# If you are using a VM or Elasticsearch exits with code 78, run this with root:
#sysctl -w vm.max_map_count=262144

# Single-node Elasticsearch
docker-compose up -d

# Multi-node Elasticsearch
docker-compose -f docker-compose-ha.yml up -d
```

## Conventions

### Style Guide

* [PEP8](https://www.python.org/dev/peps/pep-0008/)

### Branching Model

Pushing to **feature** branches and then opening a Pull Request to **master**

### Contributing

To contribute to the project, get in touch with one of the [Authors](#Authors).

## Authors

* **DE LA VEGA, Matías** - _delaVega.Matias@gmail.com_

* **FRÍAS, Pablo** - _pablosfrias@gmail.com_

* **RÍOS, Julieta** - _julirios299@gmail.com_

* **ULLA, Gonzalo** - _gonzaulla@gmail.com_
