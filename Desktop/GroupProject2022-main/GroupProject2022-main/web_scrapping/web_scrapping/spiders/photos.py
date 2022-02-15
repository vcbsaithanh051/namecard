import scrapy

class PhotosSpider(scrapy.Spider):
    name = 'photos'

    def __init__(self, *args, **kwargs): 
      super(PhotosSpider, self).__init__(*args, **kwargs) 

      self.start_urls = [kwargs.get('start_url')] 

    def parse(self, response):
        raw_image_urls = response.css('img ::attr(src)').getall()
        clean_image_urls = []
        for img_url in raw_image_urls:
            clean_image_urls.append(response.urljoin(img_url))
        
        yield {
            'image_urls': clean_image_urls
        }