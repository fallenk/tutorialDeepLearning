#  version 1
# import scrapy
# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#     def start_requests(self):
#         urls = [
#             "http://quotes.toscrape.com/page/1/",
#             "http://quotes.toscrape.com/page/2/",
#         ]
#         for url in urls:
#             yield scrapy.Request(url=url, callback = self.parse)
#     def parse(self, response):
#         page = response.url.split("/")[-2]
#         fileName = 'quotes-%s.html' % page
#         with open(fileName, 'wb') as f:
#             f.write(response.body)
#         self.log('Saved file %s' % fileName)

# version 2
# import scrapy
# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#     start_urls = [
#         "http://quotes.toscrape.com/page/1/",
#         "http://quotes.toscrape.com/page/2/"
#     ]
#     def parse(self, response):
#         page = response.url.split("/")[-2]
#         fileName = 'quotes-%s.html' % page
#         with open(fileName, 'wb') as f:
#             f.write(response.body)

# version3
# import scrapy 
# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#     start_urls = [
#         'http://quotes.toscrape.com/page/1/',
#         'http://quotes.toscrape.com/page/2/',
#     ]
#     def parse(self, response):
#         for quote in response.css('div.quote'):
#             yield {
#                 'text': quote.css('span.text::text').extract_first(),
#                 'author': quote.css('small.author::text').extract_first(),
#                 'tags': quote.css('div.tags a.tag::text').extract(),
#             }

# version4 add follow link
# import scrapy
# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#     start_urls = [
#         'http://quotes.toscrape.com/page/1/',
#     ]
#     def parse(self, response):
#         for quote in response.css('div.quote'):
#             yield {
#                 'text': quote.css('span.text::text').extract_first(),
#                 'author': quote.css('small.author::text').extract_first(),
#                 'tags': quote.css('div.tags a.tag::text').extract(),
#             }
#         next_page = response.css('li.next a::attr(href)').extract_first()
#         if next_page is not None:
#             next_page = response.urljoin(next_page)
#             yield scrapy.Request(next_page, callback=self.parse)

# version5 shortcut
# import scrapy
# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#     start_urls = [
#         'http://quotes.toscrape.com/page/1/',
#     ]
#     def parse(self, response):
#         for quote in response.css('div.quote'):
#             yield {
#                 'text': quote.css('span.text::text').extract_first(),
#                 'author': quote.css('small.author::text').extract_first(),
#                 'tags': quote.css('div.tags a.tag::text').extract(),
#             }
#         next_page = response.css('li.next a::attr(href)').extract_first()
#         if next_page is not None:
#             yield response.follow(next_page, callback=self.parse)

# version6 scrape author page and next quotes page
# import scrapy
# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#     start_urls = [
#         'http://quotes.toscrape.com/page/1/',
#     ]
#     def parse(self, response):
#         # follow links to author page
#         for href in response.css('.author + a::attr(href)'):
#             yield response.follow(href, self.parse_author)
#         # follow pagination links
#         for href in response.css('li.next a::attr(href)'):
#             yield response.follow(href, self.parse)
#     def parse_author(self, response):
#         def extract_with_css(query):
#             return response.css(query).extract_first().strip()
#         yield {
#             'name': extract_with_css('h3.author-title::text'),
#             'birthdate': extract_with_css('.author-born-date::text'),
#             'bio': extract_with_css('.author-description::text'),
#         }

# version7 
import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    def start_requests(self):
        url = 'http://quotes.toscrape.com/'
        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse)
    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
            }
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)