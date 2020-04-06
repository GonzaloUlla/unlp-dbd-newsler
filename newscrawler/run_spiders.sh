#!/bin/bash

DT_NOW=$(date +%Y%m%d_%H%M)

scrapy runspider spiders/al_jazeera_spider.py -o json/al_jazeera_spider_"${DT_NOW}".json 2>&1 \
    | tee -a logs/al_jazeera_spider_"${DT_NOW}".log

scrapy runspider spiders/cnn_spider.py -o json/cnn_spider_"${DT_NOW}".json 2>&1 \
    | tee -a logs/cnn_spider_"${DT_NOW}".log

scrapy runspider spiders/deutsche_welle_spider.py -o json/deutsche_welle_spider_"${DT_NOW}".json 2>&1 \
    | tee -a logs/deutsche_welle_spider_"${DT_NOW}".log

scrapy runspider spiders/fox_news_spider.py -o json/fox_news_spider_"${DT_NOW}".json 2>&1 \
    | tee -a logs/fox_news_spider_"${DT_NOW}".log

scrapy runspider spiders/the_guardian_spider.py -o json/the_guardian_spider_"${DT_NOW}".json 2>&1 \
    | tee -a logs/the_guardian_spider_"${DT_NOW}".log
