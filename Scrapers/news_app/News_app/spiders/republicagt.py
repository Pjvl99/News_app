import scrapy
from loguru import logger
import os
class RepublicaGTSpider(scrapy.Spider):
    name = 'republicagt'
    start_urls = ["https://republica.gt/"]

    def parse(self, response):
        try:
            fileDir = os.path.dirname(os.path.abspath(__file__))
            logger.remove(0)
            logger.add(os.path.join(fileDir, "Logs/republicagt.log"), format="{level} : {time} : {message}")
            logger.info("Starting project")
            if response.status == 200:
                container = response.css(".container a[class^='seccion__hover']")
                for nav_items in container:
                    url = nav_items.xpath("@href").get()
                    category = nav_items.css(".no-hover::text").get()
                    meta = {
                        "category": category,
                        "page": 1
                    }
                    logger.info(f"Currently in: {url} : {category}", end='\n\n')
                    if url:
                        yield response.follow(url, callback=self.get_news_items, meta=meta)
                    else:
                        logger.warning("Url not found")
            else:
                logger.error("Error in connection:", response.url)
        except Exception as e:
            logger.error(str(e))

    def get_news_items(self, response):
        try:
            logger.info(f"In category: {response.meta['category']} url: {response.url}\n\n")
            if response.status == 200:
                page = response.meta["page"]
                category = response.meta["category"]
                first_container = response.css("div[class^='container opcion'] div[class^='item']")
                for card_item in first_container:
                    url = card_item.css('.nota__media a').xpath("@href").get()
                    if url:
                        meta = {"category": category}
                        yield response.follow(url, callback=self.extract_news_item, meta=meta)
                main_container = response.css(".container div[class^='columns opcion'] > div[class^='item']")
                for card_item in main_container:
                    url = card_item.css('.nota__media a').xpath("@href").get()
                    if url:
                        meta = {"category": category}
                        yield response.follow(url, callback=self.extract_news_item, meta=meta)
                pagination = response.css(".pagination span > a")
                for pages in pagination:
                    if page == int(pages.css("a::text").get())-1:
                        url = pages.xpath("@href").get()
                        if url:
                            meta = {"category": category, "page": page+1}
                            yield response.follow(url, callback=self.get_news_items, meta=meta)
                        else:
                            logger.warning("Url not found")
                        break
            else:
                logger.error("Error in connection:", response.url)
        except Exception as e:
            logger.error(str(e))

    def extract_news_item(self, response):
        try:
            if response.status == 200:
                sub_category = response.css("span[class^='nota__volanta']::text").get(default="not-found")
                if not sub_category:
                    sub_category = "Especial"
                title = response.css(".articulo__titulo::text").get(default="not-found")
                if title:
                    images = response.css(".articulo__media > amp-img[class^='i-amphtml-layout-responsive i-amphtml-layout-size-defined']")
                    image_url = ""
                    counter = 0
                    for image in images:
                        counter += 1
                        if counter == 2:
                            image_url = image.xpath("@src").get(default="not-found")
                            break
                else:
                    title = response.css(".especial__media--titulo h1::text").get(default="not-found")
                    images = response.css(".especial__media--img > amp-img[class^='i-amphtml-layout-responsive i-amphtml-layout-size-defined']")
                    image_url = ""
                    counter = 0
                    for image in images:
                        counter += 1
                        if counter == 2:
                            image_url = image.xpath("@src").get(default="not-found")
                            break
                date = response.xpath("/html/head/meta[30]/@content")[0].extract()
                author = response.xpath("/html/head/meta[28]/@content")[0].extract()
                article_body = response.css(".articulo__cuerpo")
                description = ""
                full_description = article_body.css("p, ul, h2, div[class^='destacado_en_cuerpo'], blockquote")
                for full_description_item in full_description:
                    if not "fixed-container" in full_description_item.get():
                        description += full_description_item.get()
                yield {
                    "category": response.meta["category"],
                    "img_url": image_url,
                    "title": title,
                    "date": date,
                    "author": author,
                    "subcategory": sub_category,
                    "description": description,
                    "news_site": "republicagt"
                }
            else:
                logger.error("Error in connection:", response.url)
        except Exception as e:
            logger.error(str(e))
 