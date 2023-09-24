import scrapy
from loguru import logger
from datetime import datetime
import os
class ElSigloSpider(scrapy.Spider):
    name = "elsiglo"
    start_urls = ["https://elsiglo.com.gt/"]
    with open('variables.txt', 'r') as file:
        lines = file.readlines()
        file.close()
    first_date = lines[2].split('=')[1]
    if len(first_date) > 1:
        date = first_date.strip()
        original_date = first_date.strip()
    else:
        date = "1899-01-01"
        original_date = "1899-01-01"
    
    def parse(self, response):
        try:
            fileDir = os.path.dirname(os.path.abspath(__file__))
            logger.remove(0)
            logger.add(os.path.join(fileDir, "Logs/elsiglo.log"), format="{level} : {time} : {message}")
            logger.info("Starting project")
            if response.status == 200:
                nav_items = response.css(".menu > li > a")
                for item_level_one in nav_items:
                    href = item_level_one.xpath("@href").get()
                    category = item_level_one.css("a::text").get(default="not-found")
                    if not "elsiglo.com" in href:
                        break
                    if category != "Inicio":
                        meta = {"category": category}
                        if href:
                            yield response.follow(href, callback=self.get_news_items, meta=meta)
            else:
                logger.error("Error in connection:", response.url)
        except Exception as e:
            logger.error(str(e))
    
    def get_news_items(self, response):
        try:
            logger.info(f"In category: {response.meta['category']} url: {response.url}\n\n")
            if response.status == 200:
                posts = response.css("article[class^=' post-']")
                for post in posts:
                    img_url = post.css(".cm-featured-image > a > img").xpath("@data-src").get(default="not-found")
                    post_url = post.css(".cm-featured-image > a").xpath("@href").get()
                    title = post.css(".cm-entry-title > a").xpath("@title").get(default="not-found")
                    datetime_data = post.css("time[class^='entry-date published']").xpath("@datetime").get(default="1999-01-01T07:40:01-06:00")
                    datetime_object = datetime.fromisoformat(datetime_data)
                    if not self.check_dates(datetime_object):
                        break
                    author = post.css("a[class^='url fn n']").xpath("@title").get(default="not-found")
                    tags = post.css(".cm-post-categories")
                    subcategory = ""
                    for tag in tags:
                        subcategory = tag.css("a::text").get()
                        break
                    if post_url:
                        meta = {
                            "category": response.meta["category"],
                            "img_url": img_url,
                            "title": title,
                            "datetime_data": datetime_object.date(),
                            "author": author,
                            "subcategory": subcategory
                            }
                        yield response.follow(post_url, callback=self.get_description, meta=meta)
                page_url = response.css(".previous > a").xpath("@href").get()
                if page_url:
                    meta = {"category": response.meta["category"]}
                    yield response.follow(page_url, callback=self.get_news_items, meta=meta)
            else:
                logger.error("Error in connection:", response.url)
        except Exception as e:
            logger.error(str(e))
    
    def check_dates(self, datetime_object):
        date1 = datetime.strptime(self.date, "Y-%m-%d").date()
        date2 = datetime_object.date()
        original_date = datetime.strptime(self.original_date, "Y-%m-%d").date()
        if date2 > date1:
            self.date = str(date2)
        return date2 > original_date

    def get_description(self, response):
        try:
            if response.status == 200:
                description = response.css(".cm-entry-summary p, h2, ol")
                final_description = ""
                for item in description:
                    final_description += item.get()
                yield {
                    "category": response.meta["category"],
                    "img_url": response.meta["img_url"],
                    "title": response.meta["title"],
                    "date": response.meta["datetime_data"],
                    "author": response.meta["author"],
                    "subcategory": response.meta["subcategory"],
                    "description": final_description,
                    "news_site": "elsiglo"
                }
            else:
                logger.error("Error in connection:", response.url)
        except Exception as e:
            logger.error(str(e))

    def closed(self, reason):
        self.lines[2] = f'ELSIGLO={self.date}\n'
        with open('variables.txt', 'w') as file:
            file.writelines(self.lines)
            file.close()
        