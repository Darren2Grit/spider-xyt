# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from pyquery import PyQuery
from xzspider.itemsWriting import WritingItem
from scrapy.http.cookies import CookieJar
import re
import html


class IeltsSpokingSpider(scrapy.Spider):
    name = 'IeltsSpokingSpider'
    allowed_domains = ['zhan.com']
    # start_urls = ['http://top.zhan.com/toefl/write/alltpo.html']
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
              'Referer': 'http://i.zhan.com/'}
    custom_settings = {
        'ITEM_PIPELINES': {'xzspider.SpokingPipelines.XzSpokingPipeline': 300, }
    }

    def start_requests(self):
        return [
            Request('http://passport.zhan.com/Users/login.html', meta={'cookiejar': 1},
                    callback=self.parse)
        ]

    def parse(self, response):
        data = {'url': '',
                'username': '', 'pwd': ''}
        return [scrapy.FormRequest.from_response(response,
                                                 url='http://passport.zhan.com/UsersLogin/login.html',
                                                 meta={'cookiejar': response.meta['cookiejar']},
                                                 formdata=data,
                                                 headers=self.header,
                                                 callback=self.login_next)]

    def login_next(self, response):
        yield Request(url='http://top.zhan.com/ielts/speak/cambridge.html', meta={'cookiejar': True},
                      callback=self.parse_tpo_module)

    def parse_tpo_module(self, response):
        for selector in response.css(".tpo_list_content .tpo_list li"):
            url = selector.css("a::attr(href)").extract_first()
            yield Request(url=url, meta={'cookiejar': True}, callback=self.parse_tpo_list)

    def parse_tpo_list(self, response):
        title_name = response.css(".tpo_desc_item_list .title::text").extract()
        for index, tpo_list_selector in enumerate(response.css(".tpo_desc_item_list .tpo_desc_list")):
            for tpo_item_selector in tpo_list_selector.css(".tpo_talking_item"):
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
        body_html= html.unescape(PyQuery(response.body))
        if body_html(".ielts_reading_footer").html() is not None:
            for page_html_url in response.css(".ielts_reading_footer .posi .pages_content ul a::attr(href)").extract():
                yield Request(url=page_html_url, callback=self.parse_question_page,
                          meta={'title_name': title, 'knowledge_name': knowledge_name,
                                'write_name': write_name, 'start_url': response.meta["start_url"], 'cookiejar': True})
        else:
            question=self.parse_question(response)
            question['name'] = title
            question['question_title'] = write_name
            question['question_knowledge_name'] = knowledge_name
            yield question

    def parse_question_page(self,response):
        title = response.meta['title_name']
        knowledge_name = response.meta['knowledge_name']
        write_name = response.meta['write_name']
        question =self.parse_question(response)
        question['name'] = title
        question['question_title'] = write_name
        question['question_knowledge_name'] = knowledge_name
        yield question

    def parse_question(self,response):
        body_html = html.unescape(PyQuery(response.body))
        question_content_html = body_html(".ielts_talking_content")
        if question_content_html(".ielts_talking_desc").html() is not None:
            question_content = question_content_html(".ielts_talking_desc .talk_test_item .talk_test_text").html()
        else:
            question_content = question_content_html(
                ".ielts_talking_scroll_content .ielts_talking_scroll .nano-content .nano-content_in div").html()
        question_answer = PyQuery(response.css(".talk_pigai_content  .pigai_text div").extract()[1])("div").html()
        mp3_url = re.findall(r'https:\/\/.*?\.mp3', str(response.body))
        if len(mp3_url) > 0:
            question_audio_url = str(mp3_url[0])[str(mp3_url[0]).rindex('http'):]
        else:
            question_audio_url = ""

        question = WritingItem()
        question['question_answer'] = question_answer
        question['question_content'] = question_content
        question['question_type'] = 2
        question['question_audio_content'] = ""
        question['question_audio_url'] = question_audio_url
        question['question_article_content'] = ""
        question['question_article_content_file'] = ""
        question['question_module_type'] = 8
        question['question_audio_refer'] = response.meta['start_url']
        return question