#!/bin/bash

cd ~/Jobs/Scrapers/news_app
mkdir -p Files
python3 -m scrapy crawl soy502 -o Files/soy502.csv
python3 -m scrapy crawl republicagt -o Files/republicagt.csv
python3 -m scrapy crawl elsiglo -o Files/elsiglo.csv