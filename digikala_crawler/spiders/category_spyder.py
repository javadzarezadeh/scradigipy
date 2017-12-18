import scrapy
import re


class CommentsSpider(scrapy.Spider):
    name = "category"
    start_urls = ['https://www.digikala.com/']

    def parse(self, response):
        for href in response.xpath("//footer[@id='dk-footer']/section//div[@class='box']/ul/li/a/@href"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_following)

    def parse_following(self, response):
        for href in response.xpath("//li[@class='rootitem2']/ul/li/a/@href"):
            if (href.extract()).split('/')[1] == 'Main':
                url = 'https://www.digikala.com' + href.extract()
                yield scrapy.Request(url, callback=self.parse_following)
            else:
                url = 'https://www.digikala.com' + href.extract()
                pretty_url = re.sub(r"#!/(.*)$", '', url)
                with open('category_urls.txt', 'r') as f1:
                    if pretty_url+'\n' not in f1.readlines():
                        with open('category_urls.txt', 'a') as f2:
                            f2.write(pretty_url + '\n')
