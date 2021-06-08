# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field, loader

from scrapy.loader.processors import TakeFirst, Compose, Identity, Join


class MarriottItem(Item):
    text = Field()
    title = Field()
    date = Field()
    score = Field()
    location_score = Field()
    author = Field()
    responses = Field()


class MarriottItemLoader(loader.ItemLoader):
    default_output_processor = TakeFirst()
    default_item_class = MarriottItem

    text_out = Join()
    responses_out = Identity()
    score_out = Compose(TakeFirst(), lambda x: float(x))
    location_score_out = Compose(TakeFirst(), lambda x: float(x))
    author_out = Compose(TakeFirst(), lambda x: x.strip('none').strip())
