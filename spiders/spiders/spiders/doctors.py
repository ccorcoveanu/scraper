# -*- coding: utf-8 -*-

# Doctors spider

import re
import scrapy
from time import sleep
from scrapy.spiders import Spider
from spiders.items import DoctorItem
from scrapy.http import FormRequest

import sys
import json


class DoctorsSpider(Spider):

    name        = 'doctors'
    filename    = 'doctors.txt'
    start_urls  = [
        # 'https://google.ro'
        'https://verifiera.se/start'
        # 'https://www.hitta.se/s%C3%B6k?vad=Skogsr%C3%A5v%C3%A4gen+18+59074+Ljungsbro+Ahlman'
    ]
    handle_httpstatus_list = [429]
    state = {}

    # main parse - get main page and login
    def parse(self, response):

        if response.status == 429:
            sleep(610)


        # init item count
        self.state['item_count'] = 0
        self.state['current_page'] = 2564

    	# get _csrf input
        _csrf = response.xpath('//input[@name="_csrf"]/@value').extract_first()
        return scrapy.FormRequest.from_response(
            response,
            formdata={'LoginForm[username]': 'novumcare.johan', 'LoginForm[password]': '1oh4Nfo2', '_csrf': _csrf},
            callback=self.loadSearchPage
        )

    # now load doctor search page and get _csrf input
    def loadSearchPage(self, response):
        if response.status == 429:
            sleep(610)
        # check if login was successful by looking if we have a login form
        _form = response.xpath('//form[@id="search-form"]/@action').extract_first()
        if not _form:
            self.log("Login failed", level=log.ERROR)

        return scrapy.Request('https://verifiera.se/search/doctors', callback=self.doSearch)

    def doSearch(self, response):
        if response.status == 429:
            sleep(610)
        #get _csrf
        _csrf = response.xpath('//input[@name="_csrf"]/@value').extract_first()
        
        return scrapy.FormRequest.from_response(
            response,
            formdata={'SearchDoctorForm[name]': '', 'SearchDoctorForm[personal_id]': '', 'SearchDoctorForm[address]': '', 'SearchDoctorForm[specs]': '', 'SearchDoctorForm[age_range][from]': '', 'SearchDoctorForm[age_range][to]': '75', '_csrf': _csrf},
            callback=self.loadDoctorsList,
            dont_filter=True
        )


    def loadDoctorsList(self, response):
        if response.status == 429:
            sleep(610)
        #print response.xpath('//body//text()').extract()
        for doctor in response.xpath('//table/tbody/tr'):
            texts = doctor.xpath('./td')

            #if texts[0].xpath('./span/text()').extract_first():
            #    continue

            item = DoctorItem()
            item['name'] = texts[1].xpath('./a/text()').extract_first() if texts[1].xpath('./a/text()') else texts[1].xpath('./text()').extract_first()
            item['personal_number'] = texts[0].xpath('./a/text()').extract_first() if texts[0].xpath('./a/text()') else texts[0].xpath('./text()').extract_first()
            item['specialization'] = texts[5].xpath('./a/text()').extract_first() if texts[5].xpath('./a/text()') else texts[5].xpath('./text()').extract_first()
            item['city'] = texts[4].xpath('./a/text()').extract_first() if texts[4].xpath('./a/text()') else texts[4].xpath('./text()').extract_first()
            item['ongoing'] = texts[2].xpath('./a/text()').extract_first() if texts[2].xpath('./a/text()') else texts[2].xpath('./text()').extract_first()
            item['disciplinary'] = texts[3].xpath('./a/text()').extract_first() if texts[3].xpath('./a/text()') else texts[3].xpath('./text()').extract_first()
            item['phone_number'] = ''
            
            _doctor_details_url = texts[1].xpath('./a/@data-content').extract_first()
            
            if not _doctor_details_url:
                _doctor_details_url = texts[1].xpath('./a/@href').extract_first()

            if not _doctor_details_url:
                continue

            if item['personal_number'] == '(ej satt)':
                print 'ej satt ====================================================================================='
                continue

            item['details_url'] = _doctor_details_url

            yield item

            # yield scrapy.Request('https://verifiera.se' + _doctor_details_url, callback=self.loadViewDoctorPage, meta={'item': item}, priority=5000-self.state['current_page'])

        # if self.state['current_page'] < 5000:
        self.state['current_page'] += 1
        #sleep(10)
        yield scrapy.Request('https://verifiera.se/search/doctors?request=true&page=' + str(self.state['current_page']), callback=self.loadDoctorsList)


    def loadViewDoctorPage(self, response):

        if response.status == 429:
            sleep(610)

        _url = response.xpath('//a[@target="_blank"]/@href').extract_first()

        if not _url:
            return

        item = response.meta['item']
        item['address'] = response.xpath('//ul[contains(@class, "blocks-4")]/li[2]/text()')[1].extract().strip(' \t\n\r')
        item['phone_number'] = _url
        yield item

        #yield scrapy.Request(_url, callback=self.searchPhoneNumber, meta={'item': item}, priority=5000-self.state['current_page'])


    def searchPhoneNumber(self, response):

        #if we are on a list page, parse list and try to match by name
        if len(response.xpath('//li[contains(concat(" ", @class, " "), " result-row-person ")]')):
            # split full name from verifiera into a list to be compared with hita names
            full_name = response.meta['item']['name']
            name_parts = full_name.split(' ')
            del name_parts[-1] # delete ar)
            del name_parts[-1] # delete (50

            for user_row in response.xpath('//li[contains(concat(" ", @class, " "), " result-row-person ")]'):
                _phone = user_row.xpath('.//span[contains(concat(" ", @class, " "), " result-row-person__phone ")]/text()').extract_first().strip()

                # if not _phone:
                    # if phone is not shown inside the list, it's anyway private
                #    continue
                # match at least 2 names
                _hita_name = user_row.xpath('.//span[contains(concat(" ", @class, " "), " result-row__item-hover-visualizer ")]/text()').extract_first()
                _hita_name_parts = _hita_name.split(' ')
                
                _matches = len(list(set(name_parts).intersection(_hita_name_parts)))
                
                if ( _matches > 1 ):
                    _url = user_row.xpath('.//a[contains(concat(" ", @class, " "), " result-row__link ")]/@href').extract_first()
                    print 'name==============================================='
                    print response.meta['item']['name']
                    print 'https://www.hitta.se' + _url
                    yield scrapy.Request('https://www.hitta.se' + _url, callback=self.searchPhoneNumber, meta={'item': response.meta['item']}, priority=5000-self.state['current_page'])
                    return
            self.logItem(response.meta['item'])
            return

        # we could find a direct phone number
        #_phone_numbers = response.xpath('//a[contains(@class, "phone-number--hidden__number")]/@href').extract()
        _phone_numbers = response.xpath('//a[contains(concat(" ", @class, " "), " phone-number--hidden__number ")]/@href').extract()

        # or we could have the phone number wrapped inside a span followed by a <a> tag
        # only first a tag is of interest since the following one is something unrelated. we do not try to use a class selecor
        # on the a tag because there is no class to differentiate it from the following ones
        if not _phone_numbers:
            print response.xpath('//span[contains(concat(" ", @class, " "), " phone-number--hidden__number ")]/a[1]/@href').extract()
            #_phone_numbers = response.xpath('//span[contains(@class, "phone-number--hidden__number")]/a[1]/@href').extract()
            _phone_numbers = response.xpath('//span[contains(concat(" ", @class, " "), " phone-number--hidden__number ")]/a[1]/@href').extract()

        if not _phone_numbers:
            #check not bem methodology - without span parent
            response.xpath('//a[contains(concat(" ", @class, " "), " phone-number-hidden__number ")]/@href').extract()

        if not _phone_numbers:
            #check not bem methodology with span parent - this kind of numbers contain commercial add
            _phone_numbers = response.xpath('//span[contains(concat(" ", @class, " "), " phone-number-hidden__number ")]/a[1]/@href').extract()

        if  not _phone_numbers:
            print 'penis ==========================================================='
            print response.meta['item']['name']
            self.logItem(response.meta['item'])
            return
        response.meta['item']['phone_number'] = ', '.join(_phone_numbers)
        
        yield response.meta['item']


    def logItem(self, item):
        print 'Log item ========================================================'
        with open('other_docs.json', 'a') as f:
            #f.write('phone_number: {7}, city: {0}, specialization: {1}, address: {2}, ongoing: {3}, personal_number: {4}, disciplinary: {5}, name: {6}\n'.format(item['city'], item['specialization'], item['address'], item['ongoing'], item['personal_number'], item['disciplinary'], item['name'], 'no_phone'))
            f.write(json.dumps(item, default=lambda item: item._values))
            f.write(",\n")

    
    def parseUserList(self, response):

        # split full name from verifiera into a list to be compared with hita names
        full_name = response.meta['item']
        name_parts = full_name.split(' ')
        del name_parts[-1] # delete ar)
        del name_parts[-1] # delete (50

        for user_row in response.xpath('//li[contains(concat(" ", @class, " "), " result-row-person ")]'):
            _phone = user_row.xpath('.//span[contains(concat(" ", @class, " "), " result-row-person__phone ")]/text()').extract_first().strip()
            if not _phone:
                # if phone is not shown inside the list, it's anyway private
                continue
            # match at least 2 names
            _hita_name = user_row.xpath('.//span[contains(concat(" ", @class, " "), " result-row__item-hover-visualizer ")]/text()').extract_first()
            _hita_name_parts = _hita_name.split(' ')
            _matches = len(list(set(name_parts).intersection(_hita_name_parts)))
            
            if ( _matches > 1 ):
                _url = user_row.xpath('.//a[cotains(concat(" ", @class, " "), " result-row__link ")]/@href').extract()
                yield Request('https://www.hitta.se' + _url, callback=self.searchPhoneNumber, priority=5000-self.state['current_page'])