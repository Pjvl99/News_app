import scrapy
from loguru import logger
import os
from datetime import datetime
class Soy502Spider(scrapy.Spider):
    name = 'soy502'
    start_urls = ["https://www.soy502.com/"]
    with open('variables.txt', 'r') as file:
        lines = file.readlines()
        file.close()
    first_date = lines[0].split('=')[1]
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
            logger.add(os.path.join(fileDir, "Logs/soy502.log"), format="{level} : {time} : {message}")
            logger.info("Starting project")
            if response.status == 200:
                for item in response.css('.m-left li'): #Each sub item of top nav
                    news_html_item = item.css("li[class^='menu-tax'] a")
                    if news_html_item:
                        href = news_html_item.xpath("@href").get()
                        category = str(news_html_item.css("a::text").get())
                        if category != "podcast":
                            logger.info(f"Currently in category: {category}")
                            logger.info(f"Category link: {href}", end='\n--------------------------------\n\n')
                            meta = {"category": category}
                            if href:
                                yield response.follow(href, callback=self.get_news_items, meta=meta)
                        else:
                            logger.info("Ignoring podcasts")
            else:
                logger.error("Error loading page, please try later...", response.url)
        except Exception as e:
            logger.error(str(e))

    def get_news_items(self, response):
        try:
            logger.info(f"In category: {response.meta['category']} url: {response.url}\n\n")
            meta = {"category": response.meta['category']}
            if response.status == 200:
                left_news = response.css(".grid div[class^='row row'] > a")
                if left_news:
                    logger.info("In classic card container")
                    for item in left_news:
                        href = item.xpath("@href").get()
                        if href:
                            yield response.follow(href, callback=self.extract_news, meta=meta)
                else:
                    image_card_news = response.css(".grid-multimedia div[class^='row row']")
                    logger.info("In picture card container")
                    for card in image_card_news:
                        href = card.css('.img > a').xpath("@href").get()
                        if href:
                            yield response.follow(href, callback=self.extract_news, meta=meta)
                pages = response.css('.pager-next a')
                if pages:
                    page_url = pages.xpath("@href").get()
                    yield response.follow(page_url, callback=self.get_news_items, meta=meta)
                else:
                    logger.info(f"End of category:", end='\n\n')
                    
            else:
                print(f"Error loading page for {response.meta['category']}, url:", response.url)
        except Exception as e:
            logger.error(str(e))

    def extract_news(self, response):
        try:
            if response.status == 200:
                content = response.css('.content')
                date = content.css('.date::text').get(default="1999-01-01")
                if date != "1999-01-01":
                    date = self.convert_date(date_string=str(date))
                if not self.check_dates(date):
                    return
                items = response.css("li[class^='subsection subsection'] div > a").getall()
                sub_category = "not-found"
                if items:
                    sub_category = str(items[-1:]).split('>')[1].split('<')[0]
                title = content.css('section > h1::text').get(default="not-found")
                author = content.css('.autor li::text').get().replace("Por ", "")
                all_description_tags = content.css("div[class^='body tvads'] h2, h3, p")
                photo = str(content.css(".first-element div > img").xpath("@src").get(default="not-found"))
                is_link_valid = photo[:2]
                if is_link_valid == "//":
                    photo = photo.replace("//", "")
                description = ""
                for description_item in all_description_tags:
                    description += str(description_item.get())
                yield {
                    "category": response.meta["category"],
                    "img_url": photo,
                    "title": title,
                    "date": date,
                    "author": author,
                    "subcategory": sub_category,
                    "description": description,
                    "news_site": "soy502"
                }
            else:
                logger.info("Error loading page:", response.url)
        except Exception as e:
            logger.error(str(e))
            
    def check_dates(self, date):
        date1 = datetime.strptime(self.date, "%Y-%m-%d").date()
        date2 = datetime.strptime(date, "%Y-%m-%d").date()
        original_date = datetime.strptime(self.original_date, "%Y-%m-%d").date()
        if date2 > date1:
            self.date = str(date2)
        return date2 > original_date

    def convert_date(self, date_string):
        try:
            month_mapping = {
                'enero': "01",
                'febrero': '02',
                'marzo': '03',
                'abril': '04',
                'mayo': '05',
                'junio': '06',
                'julio': '07',
                'agosto': '08',
                'septiembre': '09',
                'octubre': '10',
                'noviembre': '11',
                'diciembre': '12'
            }
            date_parts = date_string.split()
            month_number = month_mapping[date_parts[2]]
            translated_date_string = f"{date_parts[4]}-{month_number}-{date_parts[0]}".replace(",", "")
            return translated_date_string
        except Exception as e:
            logger.error(str(e))
            return "1999-01-01"
        
    def closed(self, reason):
        self.lines[0] = f'SOY502={self.date}\n'
        with open('variables.txt', 'w') as file:
            file.writelines(self.lines)
            file.close()