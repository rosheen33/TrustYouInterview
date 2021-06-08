import re
import json
from scrapy import Selector
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule, CrawlSpider
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor

from marriott.items import MarriottItemLoader


class TurkishPortalSpider(CrawlSpider):
    name = 'turkish_portal_spider'
    allowed_domains = ['turkishexportal.com']

    start_urls = [
        'https://www.turkishexportal.com/Machinery-Industrial-Parts-Tools-Category-Path-5009?lang=en',
        'https://www.turkishexportal.com/Home-Lights-Construction-Category-Path-5008?lang=en',
        'https://www.turkishexportal.com/Auto-Transportation-Category-Path-5002?lang=en,'
        'https://www.turkishexportal.com/Electrical-Equipment-Components-Telecoms-Category-Path-5005?lang=en',
        'https://www.turkishexportal.com/Electronics-Category-Path-5004?lang=en',
        'https://www.turkishexportal.com/Metallurgy-Chemicals-Rubber-Plastics-Category-Path-5010?lang=en',
    ]

    rules = [
        Rule(
            LinkExtractor(
                restrict_css=['.main-container h5', 'h5.text-center']
            ),
        ),
        Rule(
            LinkExtractor(
                restrict_css=['.btn-danger']
            ),
            callback='parse_info'
        )
    ]

    def parse_info(self, response):
        des = ' '.join(response.css(".inner-box.fontsizelarger::text").extract())
        url = response.xpath("//a[text()='Contact']//@href").extract_first()
        yield response.follow(url, callback=self.parse_contact, meta={'des': des})

    def parse_contact(self, response):
        item = {}
        item['description'] = response.meta['des']
        item['company_name'] = response.css('.fontsizelargecompanyname a::text').extract_first()
        item['name'] = response.css('.seller-info h3::text').extract_first()
        item['address'] = response.xpath("//dt[text()='Address']//following-sibling::dd[1]//text()").extract_first('').strip()
        item['city'] = response.xpath("//dt[text()='City']//following-sibling::dd[1]//text()").extract_first()
        item['country'] = response.xpath("//dt[text()='Country']//following-sibling::dd[1]//text()").extract_first()
        item['languages'] = response.xpath("//dt[text()='Languages']//following-sibling::dd[1]//text()").extract_first()
        item['telephone'] = response.xpath("//dt[text()='Telephone']//following-sibling::dd[1]//text()").extract_first()
        item['fax'] = response.xpath("//dt[text()='Fax']//following-sibling::dd[1]//text()").extract_first()
        item['website'] = response.xpath("//dt[text()='Website']//following-sibling::dd[1]//text()").extract_first()
        item['linkedin'] = response.xpath("//dt[contains(text(), 'Linkedin')]//following::dd//a//@href").extract_first()
        yield item

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
