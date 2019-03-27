import scrapy
import re


class BicyclePartsSpider(scrapy.Spider):
    name = 'bicycleparts'
    allowed_domains = ['mr-bricolage.bg']
    start_urls = ['https://mr-bricolage.bg']

    # Функции parse и parse_auto_and_bicycles_page, откриват адреса от който се достъпва категория - велоаксесоари.
    def parse(self, response):
        page_auto_and_bicycles = response.xpath('//a[@title="Авто и велоаксесоари"]/@href').get()
        if page_auto_and_bicycles is not None:
            yield response.follow(page_auto_and_bicycles, self.parse_auto_and_bicycles_page)

    def parse_auto_and_bicycles_page(self, response):
        page_bicycles = response.xpath('//img[@title="Велоаксесоари"]/../@href').get()
        if page_bicycles is not None:
            yield response.follow(page_bicycles, self.parse_target_category)

    def parse_target_category(self, response):
        # Обхождане на всеки отделен продукт
        for href in response.css('div.product div.image a::attr(href)'):
            yield response.follow(href, self.parse_details)

        # Преминаване през всички страници на категорията
        next_page = response.css('.pagination-bar li.pagination-next a.fa-chevron-right::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_target_category)

    def parse_details(self, response):
        characteristics = dict()
        store = list()
        # Събиране на наличните характеристики
        for row in response.css('div.product-classifications table.table tbody tr'):
            characteristics[str(row.xpath('td[1]//text()').get()).strip()] = str(
                row.xpath('td[2]//text()').get()).strip()

        characteristics_get = response.css('section.product-details div#stock div.store-navigation ul li')
        if characteristics:
            # Събиране на данни за наличности
            for row in characteristics_get:
                quantity = row.css('span.store-availability span.available::text').get()
                store.append({
                    'store': str(row.css('span.pickup-store-list-entry-name::text').get()).strip(),
                    'address': str(row.css('span.pickup-store-list-entry-address::text').get()).strip(),
                    'city': str(row.css('span.pickup-store-list-entry-city::text').get()).strip(),
                    'available': int(re.search(r"\d+", quantity if quantity else '0').group())
                })

        yield {
            'title': str(response.css('section.product-single h1::text').get()).strip(),
            'price': float(str(re.findall(r"[-+]?\d*\,\d+|\d+", response.css('section.product-single p.price::text').get())[0]).replace(',', '.')),
            'image': response.css('section.product-single img::attr(src)').extract_first(),
            'characteristics': [characteristics],
            'in_store': store
        }
