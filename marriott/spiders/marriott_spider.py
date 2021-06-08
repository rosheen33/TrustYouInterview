import re
import json
from scrapy import Selector
from scrapy.http import Request
from scrapy.spiders import CrawlSpider

from marriott.items import MarriottItemLoader


class MarriottSpider(CrawlSpider):
    name = 'marriott_spider'
    allowed_domains = ['marriott.ugc.bazaarvoice.com']

    start_urls = ['https://marriott.ugc.bazaarvoice.com/6604-en_us/miaxr/reviews.djs?format=embeddedhtml&page=1&scrollToTop=true']
    next_page_url_t = 'https://marriott.ugc.bazaarvoice.com/6604-en_us/miaxr/reviews.djs?format=embeddedhtml&page={}&scrollToTop=true'

    def parse(self, response):
        yield from self.parse_pagination(response)

        data = re.findall('var materials={"BVRRRatingSummarySourceID":"(.*)}', response.text)
        if not data:
            return

        data = data[0].replace('\\n', '').replace('\\', '')

        html = Selector(text=data)
        reviews = html.css("[itemprop='review']")

        for review in reviews:
            item = MarriottItemLoader(selector=review)
            item.add_css('title', "[itemprop='name']::text")
            item.add_css('text', ".BVRRReviewText ::text")
            item.add_css('date', "[itemprop='datePublished']::attr(content)")
            item.add_css('score', "[itemprop='ratingValue']::text")
            item.add_css('location_score', ".BVRRRatingLocation .BVRRRatingNumber ::text")
            item.add_css('author', "[itemprop='author']::text")
            item.add_value('responses', self.parse_responses(review))
            yield item.load_item()

    def parse_responses(self, review):
        responses = review.css('.BVDI_COComment')

        parsed_responses = []
        for res in responses:
            parsed_responses.append({
                'text': res.css(".BVDI_COCommentText::text").extract(),
                'date': res.css(".BVDI_COCommentDateValue::text").extract_first(),
            })

        return parsed_responses

    def parse_pagination(self, response):
        pages = []
        pagination_data = re.findall('webAnalyticsConfig:({.*})', response.text)
        if not pagination_data:
            return

        num_pages = json.loads(pagination_data[0])
        num_pages = num_pages['jsonData']['numPages']

        for page in range(2, num_pages+1):
            pages.append(Request(self.next_page_url_t.format(page)))

        return pages
