import scrapy
import json
import math
import hazm
import os


class CommentsSpider(scrapy.Spider):
    name = "products"
    start_urls = [
        'https://search.digikala.com/api/SearchApi/?urlCode='
    ]

    def parse(self, response):
        with open('category_urls.txt', 'r') as f:
            category_urls = set(f.readlines())
            for c_url in category_urls:
                category = c_url.split("/")[4]
                category_name = category.split('-', 1).pop().lower()
                url = response.url + category_name
                yield scrapy.Request(url, callback=lambda response, category_name=category_name: self.make_product_urls(
                    response, category_name))

    def make_product_urls(self, response, category_name):
        jsonresponse = json.loads(response.body_as_unicode())
        number_of_pages = math.ceil(jsonresponse["hits"]["total"] / 60)
        for pg_no in range(1, number_of_pages + 1):
            url = response.url + '&pageno=' + str(pg_no)
            yield scrapy.Request(url,
                                 callback=lambda response, category_name=category_name: self.fetch_product_id(response,
                                                                                                              category_name))

    def fetch_product_id(self, response, category_name):
        jsonresponse = json.loads(response.body_as_unicode())
        for product in jsonresponse["hits"]["hits"]:
            product_id = product["_id"]
            url = 'https://api.digikala.com/Product/GetTab_Comments?aqIIO=false&aqIP=false&aqSK=0&aqTK=5000&aqSO=date&aqCI=0&aqPI=' + str(
                product_id)
            # yield scrapy.Request(url, callback=self.fetch_product_comments(response, category_name))
            yield scrapy.Request(url,
                                 callback=lambda response, category_name=category_name: self.fetch_product_comments(
                                     response, category_name))

    def fetch_product_comments(self, response, category_name):
        normalizer = hazm.Normalizer()
        jsonresponse = json.loads(response.body_as_unicode())
        for product in jsonresponse["Data"]["Item2"]["Comments"]:
            file_name = category_name + '.txt'
            with open(os.path.join('digikala_dataset', file_name), 'a') as f:
                f.write(normalizer.normalize(product["Text"]) + '\n')
