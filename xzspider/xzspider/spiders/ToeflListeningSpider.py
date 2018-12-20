# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from xzspider.itemsReading import QuestionItem
from pyquery import PyQuery
import html
import uuid
import re


class ZhandomainSpider(scrapy.Spider):
    name = 'ToeflListeningSpider'
    allowed_domains = ['zhan.com']
    start_urls = ['http://top.zhan.com/toefl/listen/alltpo.html']
    custom_settings = {
        'ITEM_PIPELINES': {'xzspider.ToeflListeningpipelines.XzToeflListeningPipeline': 200, }
    }

    def parse(self, response):
        for selector in response.css(".tpo_list_content .tpo_list li"):
            url = selector.css("a::attr(href)").extract_first()
            yield Request(url=url, callback=self.parse_tpo_list)

    def parse_tpo_list(self, response):
        title_name = response.css(".title a:first-child::text").extract()
        for index, item_list_selector in enumerate(
                response.css(".tpo_desc_content .tpo_desc_item_list .tpo_desc_list")):
            for item_selector in item_list_selector.css(".tpo_desc_item"):
                knowledge_name = item_selector.css(".item_content .item_img .item_img_tips .left::text").extract_first()
                article_title = item_selector.css(".item_content .item_text .left .item_text_en::text").extract_first()
                for i, url in enumerate(item_selector.css(".item_content .item_img a::attr(href)").extract()):
                    if i == 2:
                        yield Request(url=url, callback=self.parse_question_list_page,
                                      meta={'title': title_name[index],
                                            'knowledge_name': knowledge_name,
                                            'url': url, 'article_title': article_title})

    # 处理tpo里面知识点的阅读题
    def parse_question_list_page(self, response):
        title = response.meta['title']
        knowledge_name = response.meta['knowledge_name']
        article_title = response.meta['article_title']
        article_id = uuid.uuid1();
        for index,url in enumerate(response.css("#footer_review ul a::attr(href)").extract()):
            yield Request(url=url, callback=self.parse_question,
                          meta={'title': title, 'knowledge_name': knowledge_name,
                                'article_title': article_title, 'article_id': article_id,'question_order':index,
                                'url': response.meta['url']})

    def parse_question(self, response):
        title = response.meta['title']
        knowledge_name = response.meta['knowledge_name']
        article_id = response.meta['article_id']

        # 提取听力题目相关
        content_str = html.unescape(PyQuery(response.body))(
            ".question .question_desc .question_option .q_tit .left").text()
        if content_str is not None and content_str.find('.') != -1:
            content = content_str[content_str.index('.') + 1:]
        else:
            content = content_str
        answer = response.css(".question .question_desc .answer_content .correctAnswer span::text").extract_first()
        resolve_content = response.css(".resolve_content .desc::text").extract_first()
        option_list = []
        question_type = 0
        content_list = []
        if response.css(".question .question_desc .question_option").extract_first() is not None:
            for option_selector in response.css(".question .question_desc .question_option .ops"):
                option_str = option_selector.css("label::text").extract_first()
                if option_str is not None:
                    if option_str.index(".") != -1:
                        option_list.append(option_str[option_str.index(".") + 1:])
                    else:
                        option_list.append(option_str)
                else:
                    option_str = option_selector.xpath("text()").extract_first()
                    if option_str.index(".") != -1:
                        option_list.append(option_str[option_str.index(".") + 1:])
                    else:
                        option_list.append(option_str)
        elif response.css(".question .question_desc table::text").extract_first() is not None:
            content_str = html.unescape(PyQuery(response.body))(
                ".question .question_desc .toefl_listen_table .q_tit .left").text()
            question_type = 2
            table_html = html.unescape(PyQuery(response.body))(".question .question_desc table tbody")
            for tr_index, table_tr in enumerate(table_html.children("tr").items()):
                if tr_index > 0:
                    for td_index, table_td in enumerate(table_tr.children("td").items()):
                        if td_index == 0:
                            content_list.append("<p>" + content_str + "</p><p>" + table_td(".ops").text() + "</p>")
                else:
                    for td_index, table_td in enumerate(table_tr.children("td").items()):
                        if td_index > 0:
                            option_list.append(table_td(".name").text())

        else:
            print("Sss")

        ##提取听力原文
        article_title = response.meta['article_title']
        page_body_html = html.unescape(
            PyQuery(
                response.css(".ielts_listen_review_scroll  .nano-content .nano-content_in .article").extract_first()))
        page_article_content = []
        page_article_content_translation = []
        for page_html_p in page_body_html.children("span").items():
            if page_html_p.attr("data-translation") is not None:
                page_article_content_translation.append("<p>" + page_html_p.attr("data-translation") + "</p>")
            page_article_content.append("<p>" + page_html_p(".text").text() + "</p>")

        # 提取听力材料
        mp3_url = re.findall(r'https:\/\/.*?\.mp3', str(response.body))
        question_audio_url = ""
        if len(mp3_url) > 0:
            question_audio_url = str(mp3_url[0])[str(mp3_url[0]).rindex('http'):]
        else:
            print("sss")

        if question_type == 2:
            for index, question in enumerate(content_list):
                question = QuestionItem()
                question['name'] = title
                question['question_title'] = content_list[index]
                question['question_knowledge_name'] = knowledge_name
                question['question_answer'] = answer[index]
                question['question_content'] = option_list
                question['question_resolve_content'] = resolve_content
                question['question_article_title'] = article_title
                question['question_article_id'] = article_id
                audio_content = []
                audio_content.append("".join(page_article_content))
                question['question_article_content'] = audio_content
                audio_content_trans = []
                audio_content_trans.append("".join(page_article_content_translation))
                question['question_article_content_translation'] = audio_content_trans
                question['question_type'] = 1
                question['question_module_type'] = 5
                question['question_content_file_url_list'] = []
                question["question_audio_refer"] = response.meta["url"]
                question["question_audio_url"] = question_audio_url
                question["question_order"]=response.meta["question_order"]
                yield question
        else:
            question = QuestionItem()
            question['name'] = title
            question['question_title'] = content
            question['question_knowledge_name'] = knowledge_name
            question['question_answer'] = answer
            question['question_content'] = option_list
            question['question_resolve_content'] = resolve_content
            question['question_article_title'] = article_title
            question['question_article_id'] = article_id
            audio_content = []
            audio_content.append("".join(page_article_content))
            question['question_article_content'] = audio_content
            audio_content_trans = []
            audio_content_trans.append("".join(page_article_content_translation))
            question['question_article_content_translation'] = audio_content_trans
            question['question_type'] = 1
            question['question_module_type'] = 5
            question['question_content_file_url_list'] = []
            question["question_audio_refer"] = response.meta["url"]
            question["question_audio_url"] = question_audio_url
            question["question_order"] = response.meta["question_order"]
            yield question
