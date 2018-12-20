# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from pyquery import PyQuery
from xzspider.itemsWriting import WritingItem
from scrapy.http.cookies import CookieJar
import re
import html


class TofelSpokingSpider(scrapy.Spider):
    name = 'TofelSpokingSpider'
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
                'username': '17610551758', 'pwd': 'tt5200408'}
        return [scrapy.FormRequest.from_response(response,
                                                 url='http://passport.zhan.com/UsersLogin/login.html',
                                                 meta={'cookiejar': response.meta['cookiejar']},
                                                 formdata=data,
                                                 headers=self.header,
                                                 callback=self.login_next)]

    def login_next(self, response):
        yield Request(url='http://top.zhan.com/toefl/speak/alltpo.html', meta={'cookiejar': True},
                      callback=self.parse_tpo_module)

    def parse_tpo_module(self, response):
        for selector in response.css(".tpo_list_content .tpo_list li"):
            url = selector.css("a::attr(href)").extract_first()
            yield Request(url=url, meta={'cookiejar': True}, callback=self.parse_tpo_list)

    def parse_tpo_list(self, response):
        for tpo_list_selector in response.css(".tpo_desc_item_list"):
            title_name = tpo_list_selector.css(".title a::text").extract_first()
            for tpo_item_selector in tpo_list_selector.css(".tpo_desc_list .tpo_talking_item "):
                url = tpo_item_selector.css(".md_click::attr(href)").extract_first()
                knowledge_name = tpo_item_selector.css(".text_line .text_tit::text").extract_first()
                write_name = tpo_item_selector.css(".text::text").extract_first()
                yield Request(url=url, callback=self.parse_writing_page,
                              meta={'title_name': title_name, 'knowledge_name': knowledge_name,
                                    'write_name': write_name, 'start_url': url, 'cookiejar': True})

    def parse_writing_page(self, response):
        title = response.meta['title_name']
        knowledge_name = response.meta['knowledge_name']
        write_name = response.meta['write_name']
        article_title = html.unescape(PyQuery(response.body))(
            ".toefl_listen_review_left_content  .ielts_listen_review_scroll .nano-content .nano-content_in .article_tit").text()
        if article_title.strip() != '':
            article_title = "<p>" + article_title + "</p>";
        article_content = html.unescape(PyQuery(response.body))(
            ".toefl_listen_review_left_content  .ielts_listen_review_scroll .nano-content .nano-content_in .article").html()
        if article_content.strip() != '':
            article_content = "<p>" + article_content + "</p>"

        question_content = html.unescape(PyQuery(response.body))(
            ".toefl_listen_review_left_content   .ielts_listen_review_scroll  .nano-content .nano-content_in .ques").text()

        question_answer = html.unescape(PyQuery(response.body))(".myanswer .ansart div").html()
        mp3_url = re.findall(r'https:\/\/.*?\.mp3', str(response.body))
        if len(mp3_url) > 0:
            question_audio_url = str(mp3_url[0])[str(mp3_url[0]).rindex('http'):]
            audio_contetn=html.unescape(PyQuery(response.body))(".audiowrap ._js_box .audio_topic").html()
        else:
            question_audio_url = ""
            audio_contetn=""

        question = WritingItem()
        question['name'] = title
        question['question_title'] = write_name
        question['question_knowledge_name'] = knowledge_name
        question['question_answer'] = question_answer
        if question_content.strip() == '' and article_content is not None:
            question['question_content'] = article_content
            question['question_article_content'] = ""
        else:
            question['question_content'] = question_content
            if article_content.strip() != '':
                question['question_article_content'] = article_title + article_content

        question['question_type'] = 2
        question['question_audio_content'] = audio_contetn
        question['question_audio_url'] = question_audio_url

        question['question_article_content_file'] = ""
        question['question_module_type'] = 7
        question['question_audio_refer'] = response.meta['start_url']
        yield question
