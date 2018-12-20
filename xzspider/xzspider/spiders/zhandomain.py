# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from xzspider.itemsReading import QuestionItem
from pyquery import PyQuery
import html
import uuid


class ZhandomainSpider(scrapy.Spider):
    name = 'zhandomain'
    allowed_domains = ['zhan.com']
    start_urls = ['http://top.zhan.com/toefl/read/alltpo.html']
    custom_settings = {
        'ITEM_PIPELINES': {'xzspider.pipelines.XzspiderPipeline': 300, }
    }

    def parse(self, response):
        for selector in response.css(".tpo_list_content .tpo_list li"):
            url = selector.css("a::attr(href)").extract_first()
            yield Request(url=url, callback=self.parse_tpo_list)
            print("ss")

    def parse_tpo_list(self, response):
        title = response.css(".title a:first-child::text").extract()
        hg_list = []
        qzt_list = []
        knowledge_name_list = []
        page_div_selector = response.css(".tpo_desc_list")
        for type_selector in page_div_selector:
            hg_list_temp = []
            qzt_list_temp = []
            knowledge_name_list_temp = []
            for selector in type_selector.css(".tpo_desc_item"):
                qzt = selector.css(".item_content .item_img .qzt::attr(data-url)").extract()
                hg = selector.css(".item_content .item_img .md_click::attr(href)").extract()
                knowledge_name = selector.css(".item_content .item_img .item_img_tips .left::text").extract()
                qzt_list_temp.append(qzt)
                hg_list_temp.append(hg)
                knowledge_name_list_temp.append(knowledge_name)
            hg_list.append(hg_list_temp)
            qzt_list.append(qzt_list_temp)
            knowledge_name_list.append(knowledge_name_list_temp)
        print(hg_list)
        print(qzt_list)
        print(title)
        for i, value in enumerate(title):
            title_temp = value
            knowledge_name = knowledge_name_list[i]
            hg_url_list = hg_list[i]
            for index, hg_url in enumerate(hg_url_list):
                yield Request(url=hg_url[0], callback=self.parse_question_list_page,
                              meta={'title': title_temp, 'knowledge_name': "".join(knowledge_name[index])})

    # 处理tpo里面知识点的阅读题
    def parse_question_list_page(self, response):
        title = response.meta['title']
        knowledge_name = response.meta['knowledge_name']
        article_id = uuid.uuid1();
        for index, url in enumerate(response.css("#footer_review ul a::attr(href)").extract()):
            yield Request(url=url, callback=self.parse_question,
                          meta={'title': title, 'knowledge_name': knowledge_name, 'article_id': article_id,
                                'question_order': index})

    def parse_question(self, response):
        title = response.meta['title']
        knowledge_name = response.meta['knowledge_name']
        article_id = response.meta['article_id']
        question = QuestionItem()
        content_str = html.unescape(
            PyQuery(response.css(".question .question_desc .question_option .q_tit .left").extract_first())).html()
        content = content_str[content_str.index('.') + 1:]
        answer = response.css(".question .question_desc .answer_content .correctAnswer span::text").extract_first()
        resolve_content = response.css(".resolve_content .desc::text").extract_first()
        option_list = []
        question_type = html.unescape(PyQuery(response.body))(".question .question_desc .question_option .ops").attr(
            "class")
        if question_type.find("empis") != -1:
            content += "<p>" + response.css(
                ".question .question_desc .question_option .ops::text").extract_first() + "</p>"
            print(question_type)
        else:
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

        ##获取文章的相关内容
        article_title = response.css(".word_content  .article_tit::text").extract_first()
        article_paragraph_html_str_array = PyQuery(response.css(".article").extract_first())('div').html().split(
            "<br/><br/>")
        article_content_list = []
        article_content_translation_list = []
        flag = True  # 是否能找到自然段
        insert_flag = False
        for i, article_paragraph_html in enumerate(article_paragraph_html_str_array):
            if article_paragraph_html.strip() != "" and article_paragraph_html is not None:
                paragraph_content_list = []
                paragraph_content_translation_list = []
                article_paragraph_html = html.unescape(article_paragraph_html)
                if article_paragraph_html is not None and article_paragraph_html.strip() != '':
                    for phase_span in PyQuery(article_paragraph_html).children("span").items():
                        if phase_span.attr("data-translation") is not None:
                            paragraph_content_translation_list.append(phase_span.attr("data-translation"))
                        paragraph_content_list.append(phase_span(".text").text())
                        paragraph = phase_span(".text #ParagraphAr").attr("src")
                        insert_area = phase_span(".text").children(".insert-area").html();
                        if insert_area is not None and insert_area != '':
                            insert_flag = True
                            print(phase_span(".text").children(".insert-area").html())
                        if not paragraph is None:
                            flag = False
                            question['question_belong_paragraph'] = i + 1
                article_content_list.append("<p>" + "".join(paragraph_content_list) + "</p>")
                if len(paragraph_content_translation_list) > 0:
                    article_content_translation_list.append("".join(paragraph_content_translation_list))
        question['question_type'] = 1
        if flag:
            question['question_belong_paragraph'] = len(article_paragraph_html_str_array)
        else:
            if insert_flag:
                question['question_type'] = 6
                new_article_html = ""
                qestion_insert_area = article_content_list[question['question_belong_paragraph'] - 1]
                count = 0
                select_index = 'A'
                i = 0
                while (i < len(qestion_insert_area)):
                    if qestion_insert_area[i:i + len("[■]")] == "[■]":
                        option_list.append(select_index)
                        new_article_html += qestion_insert_area[i:i + len("[■]")] + "(" + select_index + ")"
                        select_index = chr(ord(select_index) + 1)
                        i += len("[■]")
                    else:
                        new_article_html += qestion_insert_area[i]
                        i = i + 1
                question['question_insert_content'] = new_article_html

        question['name'] = title
        question['question_title'] = content
        question['question_knowledge_name'] = knowledge_name
        question['question_answer'] = answer
        question['question_content'] = option_list
        question['question_resolve_content'] = resolve_content
        question['question_article_title'] = article_title
        question['question_article_id'] = article_id
        question['question_article_content'] = article_content_list
        question['question_article_content_translation'] = article_content_translation_list
        question['question_module_type'] = 1
        question['question_content_file_url_list'] = []
        question["question_order"] = response.meta["question_order"]
        yield question
