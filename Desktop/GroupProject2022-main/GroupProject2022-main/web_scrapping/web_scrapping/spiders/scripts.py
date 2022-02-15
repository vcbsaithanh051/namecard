class ScriptsSpider(scrapy.Spider):
    name = 'scripts'

    def __init__(self, *args, **kwargs): 
      super(ScriptsSpider, self).__init__(*args, **kwargs) 

      self.start_urls = [kwargs.get('start_url')] 

    def parse(self, response):
        yield {
            'title': response.css('h1::text').get(),
            'contents': response.css('.toclevel-1 > a > .toctext::text').getall(),
            'tags': response.css('.text::text').getall(),
        }