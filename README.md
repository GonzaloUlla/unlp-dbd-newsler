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
    - [Run with Docker](#run-with-docker)
    - [Run without Docker: news-crawler](#run-without-docker-news-crawler)
    - [Run without Docker: twitter-crawler](#run-without-docker-twitter-crawler)
  - [Data Dictionary](#data-dictionary)
    - [Component Prefixes](#component-prefixes)
    - [News Crawler Variables](#news-crawler-variables)
    - [Twitter Crawler Variables](#twitter-crawler-variables)
      - [Section 2.1: Atomic Tweet](#section-21-atomic-tweet)
      - [Section 2.2: Tweet User](#section-22-tweet-user)
      - [Section 2.3: Retweeted Tweet](#section-23-retweeted-tweet)
      - [Section 2.4: Quoted Tweet](#section-24-quoted-tweet)
      - [Section 2.5: Lists](#section-25-lists)
      - [Section 2.6: All Lists](#section-26-all-lists)
  - [Conventions](#conventions)
    - [Style Guide](#style-guide)
    - [Branching Model](#branching-model)
    - [Contributing](#contributing)
  - [Authors](#authors)

## Prerequisites

### Dependencies

- Python 3.8
  - How to install latest stable release [here](https://tecadmin.net/install-python-3-8-ubuntu/)
- Pip Packages:
  - `pip install -r requirements.txt`
- News Crawler:
  - Scrapy 2.0.1, Twisted 20.3.0, Supervisor 4.1.0
- Twitter Crawler:
  - Tweepy 3.8.0, JsonLines 1.2.0, PyEnchant 3.0.1, NLTK 3.5, TextBlob 0.15.3, Supervisor 4.1.0

### Configuration

- Create a **.env** file inside `twitter-crawler` with the following keys

```bash
CONSUMER_KEY=<KEY-WITHOUT-QUOTES>
CONSUMER_SECRET=<KEY-WITHOUT-QUOTES>
ACCESS_TOKEN=<KEY-WITHOUT-QUOTES>
ACCESS_TOKEN_SECRET=<KEY-WITHOUT-QUOTES>
```

- If you are not using Docker, remember to export the previous keys

```bash
export CONSUMER_KEY=<KEY-WITHOUT-QUOTES>
export CONSUMER_SECRET=<KEY-WITHOUT-QUOTES>
export ACCESS_TOKEN=<KEY-WITHOUT-QUOTES>
export ACCESS_TOKEN_SECRET=<KEY-WITHOUT-QUOTES>
```

- **Optional:** Set the services' logging level

```bash
export LOGGING_LEVEL=<[INFO]|DEBUG|WARN|ERROR>
```
- **Optional:** Extra configuration options as `environment` keys in Compose YML files 

## Getting Started

### Run with Docker and Elasticsearch

- Start the stack

```bash
# If you are using a VM or Elasticsearch exits with code 78, run this with root:
# sysctl -w vm.max_map_count=262144

# Single-node Elasticsearch
docker-compose up -d --build

# Single-node Elasticsearch without shipping logs to ELK
# docker-compose -f docker-compose.lite.yml up -d --build

# Multi-node Elasticsearch
# docker-compose -f docker-compose.ha.yml up -d --build
```

- Import Dashboard and default Index Pattern to Kibana

  - Go to `http://localhost:5601/`
  - Select: `Management` --> `Saved objects` --> `Import`
  - Select NDJSON file: `/path/to/unlp-dbd-newsler/elk/kibana-dashboard.ndjson`

- Set Index Patterns in Kibana

  - Go to `http://localhost:5601/`
  - Select: `Management` --> `Index Patterns`
  - Select: `logstash-data-*` --> `Set as default index` --> `Refresh field list`
  - Select:  `Management` --> `Index Patterns` --> `Create index pattern`
    - Index pattern: `logstash-logs-*`, Time Filter field name: `@timestamp`

- Explore Kibana Dashboard
  - Select: `Dashboard`
  - Select: `Dashboard_Newsler`

- Discover data in real time
  - Select: `Discover`
  - Select index: `logstash-data-*` for news and tweets (check [Data Dictionary](#data-dictionary))
  - Select index: `logstash-logs-*` for Newsler's logs


### Run with Docker and MongoDB

- Start the stack

```bash
# If you are using a VM, run this with root:
# sysctl -w vm.max_map_count=262144

# Single-node MongoDB
docker-compose -f docker-compose.mongo.yml up -d --build
```

- Wait until all services are healthy

```bash
watch -n1 docker-compose -f docker-compose.mongo.yml ps
```

- Explore data in MongoDB Express

  - Go to `localhost:8081`
  - Select database with name `newsler`
  - Select collection with name `news-crawler`
  - Select collection with name `twitter-crawler`

### Run without Docker: news-crawler

- Run all Spiders

```bash
cd news-crawler
python3.8 spiders/websites.py
```

### Run without Docker: twitter-crawler

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

## Data Dictionary

### Component Prefixes

| # | Variable | Component | Definition |
|---|----------|-----------|------------|
| 1 | news_ | news-crawler | News Crawler Variables |
| 2 | tweet_ | twitter-crawler | Twitter Crawler Variables |

### News Crawler Variables

| # | Variable | Component | Definition | Comment / Example |
|---|----------|-----------|------------|-------------------|
| 1 | news_| news-crawler | News Crawler Variables | Section 1. All news-crawler variables start with **`news_`** (`websites.py`) |
| 1.1 | news_absolute_url | news-crawler | Complete URL of each news | <https://www.cnn.com/2020/04/27/asia/cctv-cameras-china-hnk-intl/index.html> |
| 1.2 | news_base_url | news-crawler | Home URL of each news website | <https://www.cnn.com> |
| 1.3 | news_text | news-crawler | News title | Bill Gates predicts when we'll get a coronavirus vaccine |

### Twitter Crawler Variables

#### Section 2.1: Atomic Tweet

| # | Variable | Component | Definition | Comment / Example |
|---|----------|-----------|------------|-------------------|
| 2 | tweet_| twitter-crawler | Twitter Crawler Variables | Section 2. All twitter-crawler variables start with **`twitter_`** (`generators.py`) |
| 2.1 | tweet_*| twitter-crawler | Atomic Tweet Variables | Section 2.1 Base tweet variables start with `twitter_` |
| 2.1.01 | tweet_id | twitter-crawler | Tweet ID | int |
| 2.1.02 | tweet_id_str | twitter-crawler | Tweet String ID | `"1254987260522610688"` --> <https://twitter.com/user/status/1254986689296007168> |
| 2.1.03 | tweet_text | twitter-crawler | Tweet Full Text | Complete tweet text withour "RT" annotation |
| 2.1.04 | tweet_hashtags | twitter-crawler | Tweet Hashtags | JSON object |
| 2.1.05 | tweet_is_quote | twitter-crawler | Tweet Is Quote | boolean: `true|false` |
| 2.1.06 | tweet_is_retweet | twitter-crawler | Tweet Is Retweet | boolean: `true|false` |
| 2.1.07 | tweet_lang | twitter-crawler | Tweet Language | ISO 2 Letter Language Code String: `"en"` |
| 2.1.08 | tweet_likes | twitter-crawler | Tweet Like Count| Base tweet favorite count (int) |
| 2.1.09 | tweet_mentions | twitter-crawler | Tweet User Mentions | JSON object |
| 2.1.10 | tweet_retweets | twitter-crawler | Tweet Retweet Count | Base tweet favorite count (int) |
| 2.1.11 | tweet_source | twitter-crawler | Tweet Source |  |
| 2.1.12 | tweet_streaming | twitter-crawler | Tweet Streaming | Polling or streaming tweet? boolean: `true|false` |
| 2.1.13 | tweet_timestamp | twitter-crawler | Tweet Creation Time | String: `Tue Apr 28 04:11:57 +0000 2020` |
| 2.1.14 | tweet_urls | twitter-crawler | Tweet URLs | JSON object |

#### Section 2.2: Tweet User

| # | Variable | Component | Definition | Comment / Example |
|---|----------|-----------|------------|-------------------|
| 2 | tweet_| twitter-crawler | Twitter Crawler Variables | Section 2. All twitter-crawler variables start with **`twitter_`** (`generators.py`) |
| 2.2 | tweet_user_*| twitter-crawler | Tweet User Variables | Section 2.2 Tweet user variables start with `twitter_user_` |
| 2.2.01 | tweet_user_id | twitter-crawler | Tweet User ID | int |
| 2.2.02 | tweet_user_name | twitter-crawler | Tweet User Name | `"screen_name"` |
| 2.2.03 | tweet_user_creation_timestamp | twitter-crawler | Tweet User Creation Time | String: `Tue Apr 28 04:11:57 +0000 2020` |
| 2.2.04 | tweet_user_description | twitter-crawler | Tweet User Description | String |
| 2.2.05 | tweet_user_followers | twitter-crawler | Tweet User Follower Count | int |
| 2.2.06 | tweet_user_following | twitter-crawler | Tweet User Following Count | int |
| 2.2.07 | tweet_user_location | twitter-crawler | Tweet User Location | `"Kent, UK"` |
| 2.2.08 | tweet_user_tweets | twitter-crawler | Tweet User Tweets Count | int |
| 2.2.09 | tweet_user_verified | twitter-crawler | Tweet User Verified | boolean: `true|false` |

#### Section 2.3: Retweeted Tweet

| # | Variable | Component | Definition | Comment / Example |
|---|----------|-----------|------------|-------------------|
| 2 | tweet_| twitter-crawler | Twitter Crawler Variables | Section 2. All twitter-crawler variables start with **`twitter_`** (`generators.py`) |
| 2.3 | tweet_retweeted_*| twitter-crawler | Retweeted Tweet Variables | Section 2.3 Retweeted tweet variables start with `twitter_retweeted_` |
| 2.3.01 | tweet_retweeted_id | twitter-crawler | Retweeted Tweet ID | int |
| 2.3.02 | tweet_retweeted_id_str | twitter-crawler | Retweeted Tweet String ID | `"1254830676215554049"` --> <https://twitter.com/user/status/1254830676215554049> |
| 2.3.03 | tweet_retweeted_text | twitter-crawler | Retweeted Tweet Full Text | Complete tweet text withour "RT" annotation |
| 2.3.04 | tweet_retweeted_hashtags | twitter-crawler | Retweeted Tweet Hashtags | JSON object |
| 2.3.05 | tweet_retweeted_likes | twitter-crawler | Retweeted Tweet Like Count | int |
| 2.3.06 | tweet_retweeted_mentions | twitter-crawler | Retweeted Tweet User Mentions | JSON object |
| 2.3.07 | tweet_retweeted_retweets | twitter-crawler | Retweeted Retweet Count | int |
| 2.3.08 | tweet_retweeted_urls | twitter-crawler | Retweeted Tweet Tweet URLs | JSON object |
| 2.3.09 | tweet_retweeted_user_id | twitter-crawler | Retweeted Tweet User ID | int |
| 2.3.10 | tweet_retweeted_user_name | twitter-crawler | Retweeted Tweet User Name | `"screen_name"` |

#### Section 2.4: Quoted Tweet

| # | Variable | Component | Definition | Comment / Example |
|---|----------|-----------|------------|-------------------|
| 2 | tweet_| twitter-crawler | Twitter Crawler Variables | Section 2. All twitter-crawler variables start with **`twitter_`** (`generators.py`) |
| 2.4 | tweet_quoted_*| twitter-crawler | Quoted Tweet Variables | Section 2.4 Quoted tweet variables start with `twitter_quoted_` |
| 2.4.01 | tweet_quoted_id | twitter-crawler | Quoted Tweet ID | int |
| 2.4.02 | tweet_quoted_id_str | twitter-crawler | Quoted Tweet String ID | `"1254734831340183552"` --> <https://twitter.com/user/status/1254734831340183552> |
| 2.4.03 | tweet_quoted_text | twitter-crawler | Quoted Tweet Full Text | Complete tweet text withour "RT" annotation |
| 2.4.04 | tweet_quoted_hashtags | twitter-crawler | Quoted Tweet Hashtags | JSON object |
| 2.4.05 | tweet_quoted_likes | twitter-crawler | Quoted Tweet Like Count | int |
| 2.4.06 | tweet_quoted_mentions | twitter-crawler | Quoted Tweet User Mentions | JSON object |
| 2.4.07 | tweet_quoted_retweets | twitter-crawler | Quoted Retweet Count | int |
| 2.4.08 | tweet_quoted_urls | twitter-crawler | Quoted Tweet Tweet URLs | JSON object |
| 2.4.09 | tweet_quoted_user_id | twitter-crawler | Quoted Tweet User ID | int |
| 2.4.10 | tweet_quoted_user_name | twitter-crawler | Quoted Tweet User Name | `"screen_name"` |

#### Section 2.5: Lists

| # | Variable | Component | Definition | Comment / Example |
|---|----------|-----------|------------|-------------------|
| 2 | tweet_| twitter-crawler | Twitter Crawler Variables | Section 2. All twitter-crawler variables start with **`twitter_`** (`generators.py`) |
| 2.5 | tweet_*_list| twitter-crawler | Tweet Lists Variables | Section 2.5 Tweet lists variables end with `_list` |
| 2.5.01 | tweet_hashtags_list | twitter-crawler | Base Tweet Hashtag List | String `"hastag1, hastag2, "` |
| 2.5.02 | tweet_mentions_list | twitter-crawler | Base Tweet Mentions List | String `"user1, user2, "` |
| 2.5.03 | tweet_urls_list | twitter-crawler | Base Tweet Urls List | String `"url1, url2, "` |
| 2.5.04 | tweet_retweeted_hashtags_list | twitter-crawler | Retweeted Tweet Hashtag List | String `"hastag1, hastag2, "` |
| 2.5.05 | tweet_retweeted_mentions_list | twitter-crawler | Retweeted Tweet Mentions List | String `"user1, user2, "` |
| 2.5.06 | tweet_retweeted_urls_list | twitter-crawler | Retweeted Tweet Urls List | String `"url1, url2, "` |
| 2.5.07 | tweet_quoted_hashtags_list | twitter-crawler | Quoted Tweet Hashtag List | String `"hastag1, hastag2, "` |
| 2.5.08 | tweet_quoted_mentions_list | twitter-crawler | Quoted Tweet Mentions List | String `"user1, user2, "` |
| 2.5.09 | tweet_quoted_urls_list | twitter-crawler | Quoted Tweet Urls List | String `"url1, url2, "` |

#### Section 2.6: All Lists

| # | Variable | Component | Definition | Comment / Example |
|---|----------|-----------|------------|-------------------|
| 2 | tweet_| twitter-crawler | Twitter Crawler Variables | Section 2. All twitter-crawler variables start with **`twitter_`** (`generators.py`) |
| 2.6 | tweet_*_list_all| twitter-crawler | Tweet All Lists Variables | Section 2.6 Tweet all lists variables end with `_list_all` |
| 2.6.01 | tweet_hashtags_list_all | twitter-crawler | Tweeted, Retweeted and Quoted Hashtag List | String `"hastag1, hastag2, "` containing all hashtags in `tweet_hashtag_list`, `tweet_retweeted_hashtag_list` and `tweet_quoted_hashtag_list` |
| 2.6.02 | tweet_mentions_list_all | twitter-crawler | Tweeted, Retweeted and Quoted Tweet Mentions List | String `"user1, user2, "` containing all users in `tweet_mentions_list`, `tweet_retweeted_mentions_list` and `tweet_quoted_mentions_list` |
| 2.6.03 | tweet_urls_list_all | twitter-crawler | Tweeted, Retweeted and Quoted Tweet Urls List | String `"url1, url2, "` containing all urls in `tweet_urls_list`, `tweet_retweeted_urls_list` and `tweet_quoted_urls_list` |

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
