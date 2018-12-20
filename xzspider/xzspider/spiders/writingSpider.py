# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from pyquery import PyQuery
from xzspider.itemsWriting import WritingItem
from scrapy.http.cookies import CookieJar
import re
import html


class WritingspiderSpider(scrapy.Spider):
    name = 'writingSpider'
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
       yield Request(url='http://top.zhan.com/toefl/write/alltpo.html', meta={'cookiejar': True},
                      callback=self.parse_tpo_module)

    def parse_tpo_module(self, response):
        for index,selector in enumerate(response.css(".tpo_list_content .tpo_list li")):
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
        question_content = response.css(".inside .title_text .tigan::text").extract_first()
        question_answer = response.css(
            "#sxk .nano-content .nano-content_in .fanwen1content .answer_textarea .fanwen::text").extract_first()
        question_audio_content=html.unescape(PyQuery(response.body))(".audio ._js_box .audio_topic").html();
        #question_audio_content = response.css(".audio ._js_box .audio_topic p::text").extract_first()
        question_audio_url = response.css(".audio #listen_review_audio audio::attr(src)").extract_first()
        mp3_url = re.findall(r'https:\/\/.*?\.mp3', str(response.body))
        if len(mp3_url) > 0:
            question_audio_url = str(mp3_url[0])[str(mp3_url[0]).rindex('https'):]
        question_article_html = PyQuery(response.css("#kmyw .nano-content .nano-content_in .article").extract_first())
        question_article_content_file = []
        length = question_article_html('div').children().length
        question_article_content = question_article_html('div').html()
        if length > 0:
            # html = question_article_html('div').html()
            pattern = re.compile('<img[^>]*/>')
            question_article_content = re.sub(pattern, '$img', question_article_content)
            for question_article_img in question_article_html('div').children("img").items():
                question_article_content_file.append(question_article_img.attr("src"))

        question = WritingItem()
        question['name'] = title
        question['question_title'] = write_name
        question['question_knowledge_name'] = knowledge_name
        question['question_answer'] = question_answer
        question['question_content'] = question_content
        question['question_type'] = 3
        question['question_audio_content'] = question_audio_content
        question['question_audio_url'] = question_audio_url
        question['question_article_content'] = question_article_content
        question['question_article_content_file'] = question_article_content_file
        question['question_audio_refer'] = response.meta['start_url']
        yield question
