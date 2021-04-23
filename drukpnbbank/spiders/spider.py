import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import DdrukpnbbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class DdrukpnbbankSpider(scrapy.Spider):
	name = 'drukpnbbank'
	start_urls = ['https://www.drukpnbbank.bt/category/latest-news-updates/']

	def parse(self, response):
		articles = response.xpath('//div[@class="serviceBox"]')
		for article in articles:
			date = article.xpath('.//h3/following-sibling::text()[1]').get().split('on ')[1]
			post_links = article.xpath('.//a[@class="read-more"]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="col-md-12 col-lg-8 text-justify my-content"]//text()[not(ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))
		if not content:
			content = "Image in the provided link"

		item = ItemLoader(item=DdrukpnbbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
