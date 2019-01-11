# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from pyquery import PyQuery
from xzspider.itemsWriting import WritingItem
from scrapy.http.cookies import CookieJar
import re


class WritingspiderSpider(scrapy.Spider):
    name = 'writingSpiderOfIELTS'
    allowed_domains = ['zhan.com']
    # start_urls = ['http://top.zhan.com/toefl/write/alltpo.html']
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
              'Referer': 'http://i.zhan.com/'}
    custom_settings = {
        'ITEM_PIPELINES': {'xzspider.writingPipelines.XzWritingPipeline': 300, }
    }

    def start_requests(self):
        return [
            Request('http://passport.zhan.com/Users/login.html', meta={'cookiejar': 1},
                    callback=self.parse)
        ]

    def parse(self, response):
        data = {'url': '',
                'username': '', 'pwd': ''}
        cookie_jar = CookieJar()
        return [scrapy.FormRequest.from_response(response,
                                                 url='http://passport.zhan.com/UsersLogin/login.html',
                                                 meta={'cookiejar': response.meta['cookiejar']},
                                                 formdata=data,
                                                 headers=self.header,
                                                 callback=self.login_next)]

    def login_next(self, response):
        yield Request(url='http://top.zhan.com/ielts/write/cambridge.html', meta={'cookiejar': True},
                      callback=self.parse_tpo_module)
        '''yield Request(url='http://top.zhan.com/toefl/write/alltpo.html', meta={'cookiejar': True},
                      callback=self.parse_tpo_module)'''

    def parse_tpo_module(self, response):
        for selector in response.css(".tpo_list_content .tpo_list li"):
            url = selector.css("a::attr(href)").extract_first()
            yield Request(url=url, meta={'cookiejar': True}, callback=self.parse_tpo_list)

    def parse_tpo_list(self, response):
        title_name = response.css(".tpo_desc_item_list .title::text").extract()
        for index,tpo_list_selector in enumerate(response.css(".tpo_desc_item_list .tpo_desc_list")):
            for tpo_item_selector in tpo_list_selector.css(".tpo_talking_item "):
                url = tpo_item_selector.css(".blue::attr(href)").extract_first()
                knowledge_name = tpo_item_selector.css(".text_line .text_tit::text").extract_first()
                write_name = tpo_item_selector.css(".text::text").extract_first()
                yield Request(url=url, callback=self.parse_writing_page,
                              meta={'title_name': title_name[index], 'knowledge_name': knowledge_name,
                                    'write_name': write_name, 'start_url': url, 'cookiejar': True})

    def parse_writing_page(self, response):
        title = response.meta['title_name']
        knowledge_name = response.meta['knowledge_name']
        write_name = response.meta['write_name']
        response_html = PyQuery(response.body)
        question_answer=response_html("#sxk .nano-content .nano-content_in .fanwencontent .answer_textarea .noedit").html()
        question_article_html = response_html("#kmyw .nano-content .nano-content_in").html()
        question_article_content_file = []
        img_list=re.findall('<img[^>]*/>',question_article_html);
        if len(img_list)>0:
            pattern=re.compile('<img[^>]*/>')
            question_article_html=re.sub(pattern,'$img',question_article_html)
            for img in img_list:
                img_url=PyQuery(img).attr("src")
                question_article_content_file.append(img_url)
                print(img_url)
        question = WritingItem()
        question['name'] = title
        question['question_title'] = write_name
        question['question_knowledge_name'] = knowledge_name
        question['question_answer'] = question_answer
        question['question_type'] = 4
        question['question_article_content'] = question_article_html
        question['question_article_content_file'] = question_article_content_file
        question['question_audio_refer'] = response.meta['start_url']
        question['question_audio_url']=None
        yield question
