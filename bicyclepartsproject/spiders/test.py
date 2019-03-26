import scrapy


class BicyclePartsSpider(scrapy.Spider):
    name = 'test'

    start_urls = ['https://mr-bricolage.bg/bg/Каталог/Инструменти/Авто-и-велоаксесоари/Велоаксесоари/c/006008012', ]

    def parse(self, response):
        for prod in response.css('div.product'):
            yield {
                'product': str(prod.css('div.title a.name::text').get()).replace('\n\t\t\t\t\t', ''),
            }

        next_page = response.css('li.pagination-next a.fa-chevron-right::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
