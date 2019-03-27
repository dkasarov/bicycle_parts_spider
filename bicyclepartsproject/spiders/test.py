import scrapy
import re


# Тестване на отделни модули от bicycle_parts_spider
class BicyclePartsSpider(scrapy.Spider):
    name = 'test'

    start_urls = ['https://mr-bricolage.bg/bg/Instrumenti/Avto-i-veloaksesoari/Veloaksesoari/UNIVERSALNO-ZhILO-ZA-SKOROSTI-FISHER/p/986371', ]

    def parse(self, response):
        for row in response.css('section.product-details div#stock div.store-navigation ul li'):
            quantity = row.css('span.store-availability span.available::text').get()
            yield {
                'store': str(row.css('span.pickup-store-list-entry-name::text').get()).strip(),
                'address': str(row.css('span.pickup-store-list-entry-address::text').get()).strip(),
                'city': str(row.css('span.pickup-store-list-entry-city::text').get()).strip(),
                'available': int(re.search(r"\d+", quantity if quantity else '0').group())
            }
