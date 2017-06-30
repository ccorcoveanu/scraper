# -*- coding: utf-8 -*-

# Emag spider

import re
import scrapy
from scrapy.spiders import Spider

class HitaSpider(Spider):
    name        = 'hita'
    filename    = 'hita.txt'
    start_urls  = [
        'https://www.hitta.se/gerasimos+afendras/%C3%A4lvsj%C3%B6/person/~WsXvUqqko?vad=Eldsbergagr%C3%A4nd+2+lgh+1202+12573+%C3%84lvsj%C3%B6+Afendras'
    ]

    def parse(self, response):
        print 'callback'
        _tels = response.xpath('//a[contains(@class, "phone-number--hidden__number")]/@href').extract()
        print ', '.join(_tels)