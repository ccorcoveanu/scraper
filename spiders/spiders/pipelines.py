# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonLinesItemExporter

class SpidersPipeline(object):
    def process_item(self, item, spider):
        return item

class MyJsonLinesItemExporter(JsonLinesItemExporter):
    def __init__(self, file, **kwargs):
        super(MyJsonLinesItemExporter, self).__init__(file, ensure_ascii=False, **kwargs)
