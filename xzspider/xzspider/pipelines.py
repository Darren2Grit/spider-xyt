# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.files import FilesPipeline
import pymongo
from xzspider.mangoDbUtil import mangoDbUtil
from urllib.parse import urlparse
from os.path import basename, dirname, join
import scrapy
from w3lib.url import safe_url_string



class XzspiderPipeline(FilesPipeline):
    client = mangoDbUtil("reading")

    def get_media_requests(self, item, info):
        for url in item['question_content_file_url_list']:
            yield scrapy.Request(url)

    def file_path(self, request, response=None, info=None):
        path = urlparse(request.url).path
        return join(basename(dirname(path)), basename(path))

    def item_completed(self, results, item, info):
        if len(results) > 0:
            for result in results:
                if result[0]:
                    url = result[1]['url']
                    path = result[1]['path']
                    if len(item['question_content_file_url_list']) > 0:
                        for index, file in enumerate(item['question_content_file_url_list']):
                            if safe_url_string(file) == url:
                                article_html = item['question_content'][0]
                                count = 0
                                new_article_html = ""
                                new_article_html_list=[]
                                for i in range(len(article_html) - 1):
                                    if article_html[i:i + len("$img")] == "$img":
                                        if count == index:
                                            new_article_html = article_html[:i]
                                            path_new = str(path).replace("\\", "/")
                                            new_article_html += "<img src='upload/upload/img/" + path_new + "'/>"
                                            new_article_html += article_html[i + len("$img"):]
                                            new_article_html_list.append(new_article_html)
                                            item['question_content'] = new_article_html_list
                                            break
                                        else:
                                            count += 1

        data = dict(item)
        self.client.insert(data)
        return item
