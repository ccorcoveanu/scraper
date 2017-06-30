# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class EmagItem(Item):
    # define the fields for your item here like:
    title       = Field()
    image		= Field()
    url			= Field()
    brand       = Field()
    price       = Field()
    categories  = Field()
    seller      = Field()
    status      = Field()

class DoctorItem(Item):
    # define the fields for doctors
    name            = Field()
    personal_number = Field()
    specialization  = Field()
    city            = Field()
    address         = Field()
    ongoing         = Field()
    disciplinary    = Field()
    phone_number    = Field()
    details_url     = Field()