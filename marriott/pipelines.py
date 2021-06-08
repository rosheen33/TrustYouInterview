# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MarriottPipeline(object):
    # Pipeline to remove the empty fields from an item

    def process_item(self, item, spider):
        item_copy = item.copy()
        for field, value in item_copy.items():
            if not value:
                item.pop(field)
        return item
