import scrapy
import re


# Тестване на отделни модули от bicycle_parts_spider
class BicyclePartsSpider(scrapy.Spider):
    name = 'test'

    start_urls = ['https://mr-bricolage.bg/', ]

    def parse(self, response):
        page_auto_and_bicycles = response.xpath('//a[@title="Авто и велоаксесоари"]/@href').get()
        if page_auto_and_bicycles is not None:
            yield response.follow(page_auto_and_bicycles, self.parse_auto_and_bicycles_page)

    def parse_auto_and_bicycles_page(self, response):
        page_bicycles = response.xpath('//img[@title="Велоаксесоари"]/../@href').get()
        if page_bicycles is not None:
            yield {
                'page': page_bicycles
            }
