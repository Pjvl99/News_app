#!/bin/bash

cd ~/Jobs/Scrapers/news_app
mkdir -p Files
mkdir -p News_app/spiders/Logs
python3 -m scrapy crawl soy502 -o soy502.csv
python3 -m scrapy crawl republicagt -o republicagt.csv
python3 -m scrapy crawl elsiglo -o elsiglo.csv
mv soy502.csv Files/soy502.csv
mv republicagt.csv Files/republicagt.csv
mv elsiglo.csv Files/elsiglo.csv