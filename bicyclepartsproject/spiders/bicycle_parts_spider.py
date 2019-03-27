import scrapy
import re


class BicyclePartsSpider(scrapy.Spider):
    name = 'bicycleparts'
    allowed_domains = ['mr-bricolage.bg']
    start_urls = ['https://mr-bricolage.bg/bg/Каталог/Инструменти/Авто-и-велоаксесоари/Велоаксесоари/c/006008012']

    def parse(self, response):
        # Обхождане на всеки отделен продукт
        for href in response.css('div.product div.image a::attr(href)'):
            yield response.follow(href, self.parse_details)

        # Преминаване през всички страници на категорията
        next_page = response.css('.pagination-bar li.pagination-next a.fa-chevron-right::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_details(self, response):
        characteristics = dict()
        store = dict()
        # Събиране на наличните характеристики
        for row in response.css('div.product-classifications table.table tbody tr'):
            characteristics[str(row.xpath('td[1]//text()').get()).strip()] = str(
                row.xpath('td[2]//text()').get()).strip()

        # Събиране на данни за наличности
        for row in response.css('section.product-details div#stock div.store-navigation ul li'):
            quantity = row.css('span.store-availability span.available::text').get()
            store = {
                'store': str(row.css('span.pickup-store-list-entry-name::text').get()).strip(),
                'address': str(row.css('span.pickup-store-list-entry-address::text').get()).strip(),
                'city': str(row.css('span.pickup-store-list-entry-city::text').get()).strip(),
                'available': int(re.search(r"\d+", quantity if quantity else '0').group())
            }

        yield {
            'title': str(response.css('section.product-single h1::text').get()).strip(),
            'price': float(str(re.findall(r"[-+]?\d*\,\d+|\d+", response.css('section.product-single p.price::text').get())[0]).replace(',', '.')),
            'image': response.css('section.product-single img::attr(src)').extract_first(),
            'characteristics': [characteristics],
            'in_store': [store]
        }
