# -*- coding: utf-8 -*-

# Emag spider

import re
import scrapy
from scrapy.spiders import Spider
from spiders.items import EmagItem

class EmagSpider(Spider):

    name        = 'emag'
    filename    = 'emag.txt'
    start_urls  = [
        'http://www.emag.ro/all-departments?ref=hdr_mm_14'
    ]
    special_header = {'X-HTTP-FORWARDED-FOR': '127.0.0.1'}

    # Main parsing 
    def parse(self, response):

        for item in response.xpath('//div[@id="department-expanded"]/ul/li/ul/li/a/@href'):
            url = response.urljoin(item.extract())
            yield scrapy.Request(url, callback=self.parseList)

    # Parse a page of items
    #
    # Takes each element of a page and parses it's details
    # Then takes the next page if there is any
    def parseList(self, response):

        for item in response.xpath('//a[@class="link_imagine "]/@href'):
            url = response.urljoin(item.extract())
            yield scrapy.Request(url, callback=self.parseDetails)

        next_item = response.xpath('//span[@class="emg-pagination-no emg-pagination-selected"]/following-sibling::a/@href').extract_first()

        if not next_item: 
            return

        yield scrapy.Request(response.urljoin(next_item), callback=self.parseList)

    # Parse product details page
    def parseDetails(self, response):

        seller          = response.xpath('//div[@class="vendor-name"]/span/text()').extract_first()
        categories      = response.xpath('//span[@itemprop="itemListElement"]/a/span/text()').extract()
        value_int       = response.xpath('//span[@class="money-int"]/text()').extract_first().replace(".", "")
        value_decimal   = response.xpath('//span[@class="money-int"]/following-sibling::sup/text()').extract_first()

        if not seller:
            seller = response.xpath('//div[@class="vendor-name"]/a/text()').extract_first()

        # Boolean representation for 'in stock' property
        status = 0
        if response.xpath('//span[@class="stock-info-box in_stock"]').extract_first():
            status = 1

        # Build the item that will be saved in the json document
        item                    = EmagItem()
        item['seller']          = seller
        item['status']          = status
        item['url']             = response.url
        item['categories']      = categories[1].strip()
        item['price']           = str(value_int) + "." + str(value_decimal)
        item['title']           = response.xpath('//h1[@class="product-title"]/text()').extract_first().strip()
        item['brand']           = response.xpath('//div[@class="disclaimer-section"]/p/a/text()').extract_first()
        item['image']           = response.xpath('//div[@id="product-pictures-content"]//img[1]/@src').extract_first()
        yield item
        #item['description'] = response.xpath('//div[@class="description-section"]/div[@class="description-content"]').extract_first()
