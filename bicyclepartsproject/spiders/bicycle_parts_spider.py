import scrapy
import re


class BicyclePartsSpider(scrapy.Spider):
    name = 'bicycleparts'
    allowed_domains = ['mr-bricolage.bg']
    start_urls = ['https://mr-bricolage.bg/bg/Каталог/Инструменти/Авто-и-велоаксесоари/Велоаксесоари/c/006008012']

    def parse(self, response):
        for href in response.css('div.product div.image a::attr(href)'):
            yield response.follow(href, self.parse_details)

        next_page = response.css('.pagination-bar li.pagination-next a.fa-chevron-right::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_details(self, response):
        characteristics = dict()
        store = dict()
        for row in response.css('div.product-classifications table.table tbody tr'):
            characteristics[str(row.xpath('td[1]//text()').get()).strip()] = str(
                row.xpath('td[2]//text()').get()).strip()

        for row in response.css(
                'div.store-navigation ul.pickup-store-list li.pickup-store-list-entry'):
            store = {
                'store': str(row.css(
                    'label.js-select-store-label span.pickup-store-info span.pickup-store-list-entry-name::text').get()).strip(),
                'address': str(
                    row.css(
                        'js-select-store-label span.pickup-store-info span.pickup-store-list-entry-address::text').get()).strip(),
                'city': str(row.css(
                    'js-select-store-label span.pickup-store-info span.pickup-store-list-entry-city::text').get()).strip(),
                'available': int(
                    re.search(r"\d+", row.css('span.store-availability span.available::text').get()).group())
            }

        yield {
            'title': str(response.css('section.product-single h1::text').get()).strip(),
            'price': float(str(re.findall(r"[-+]?\d*\,\d+|\d+",
                                          response.css('section.product-single p.price::text').get())[0]).replace(',',
                                                                                                                  '.')),
            'image': response.css('div.owl-item > img::attr(src)').extract(),
            'characteristics': [characteristics],
            'store': [store]
        }
