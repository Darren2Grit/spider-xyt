# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from xzspider.itemsReading import QuestionItem
from pyquery import PyQuery
import html
import re
import uuid


class IeltsReadingSpider(scrapy.Spider):
    name = 'leltsListeningSpider'
    allowed_domains = ['zhan.com']
    start_url = "http://top.zhan.com"
    start_urls = ['http://top.zhan.com/ielts/read/cambridge.html']
    custom_settings = {
        'ITEM_PIPELINES': {'xzspider.IeltsListeningpipelines.XzIeltsListeningPipeline': 200, }
    }
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
              'Referer': 'http://i.zhan.com/'}

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
        yield Request(url='http://top.zhan.com/ielts/listen/cambridge.html', meta={'cookiejar': True},
                      callback=self.parse_tpo_module)
        '''yield Request(url='http://top.zhan.com/toefl/write/alltpo.html', meta={'cookiejar': True},
                      callback=self.parse_tpo_module)'''

    def parse_tpo_module(self, response):
        for selector in response.css(".tpo_list_content .tpo_list li"):
            url = self.start_url + selector.css("a::attr(href)").extract_first()
            yield Request(url=url, callback=self.parse_ielts_list, meta={'cookiejar': True})

    def parse_ielts_list(self, response):
        title_type = response.css(
            ".toefl_choose_tpo_desc_content .tpo_list_content .tpo_list .active a::text").extract_first()
        title_name = response.css(".tpo_desc_content .tpo_desc_item_list .title::text").extract()
        for index, item_list_selector in enumerate(
                response.css(".tpo_desc_content .tpo_desc_item_list .tpo_desc_list")):
            for item_selector in item_list_selector.css(".tpo_desc_item"):
                knowledge_name = item_selector.css(".item_content .item_img .item_img_tips .left::text").extract_first()
                for i, url in enumerate(item_selector.css(".item_content .item_img a::attr(href)").extract()):
                    if i == 2:
                        yield Request(url=url, callback=self.parse_ielts_page,
                                      meta={'title_type': title_type, 'title_name': title_name[index],
                                            'knowledge_name': knowledge_name, 'cookiejar': True, 'url': url})

    def parse_ielts_page(self, response):
        title_type = response.meta['title_type']
        title_name = response.meta['title_name']
        knowledge_name = response.meta['knowledge_name']
        page_body_html = html.unescape(
            PyQuery(
                response.css(".ielts_listen_review_scroll .nano-content .nano-content_in .article").extract_first()))
        page_article_content = []
        page_article_content_translation = []
        for page_html_p in page_body_html.children("span").items():
            if page_html_p.attr("data-translation") is not None:
                page_article_content_translation.append("<p>" + page_html_p.attr("data-translation") + "</p>")
            page_article_content.append("<p>" + page_html_p(".text").text() + "</p>")
        article_id = uuid.uuid1()

        mp3_url = re.findall(r'https:\/\/.*?\.mp3', str(response.body))
        question_audio_url = ""
        if len(mp3_url) > 0:
            question_audio_url = str(mp3_url[0])[str(mp3_url[0]).rindex('http'):]
        else:
            print("sss")

        question_cointainer_html = html.unescape(PyQuery(
            response.css(
                ".toefl_listen_review_right_content   .ielts_listen_review_scroll  .nano-content .nano-content_in .question").extract_first()))
        # 第一种处理nano-content 包含nano-content_in、question、item等多个情况
        # 首先判断是否包含question
        for question_html in question_cointainer_html.children(".question").items():
            question = self.parse_question_html(question_html, response)
            question["module"] = title_type
            question["name"] = title_name
            question["question_knowledge_name"] = knowledge_name
            page_article_content_arr = []
            page_article_content_arr.append("".join(page_article_content))
            question["question_article_content"] = page_article_content_arr
            question["question_article_content_translation"] = page_article_content_translation
            question["question_article_id"] = article_id
            question["question_module_type"] = 6
            question["question_audio_url"] = question_audio_url
            question["question_audio_refer"] = response.meta["url"]
            yield question
        # 处理item
        for item_html in question_cointainer_html.children(".item").items():
            question_list = self.parse_item_html(item_html, response)
            for question1 in question_list:
                question1["module"] = title_type
                question1["name"] = title_name
                question1["question_knowledge_name"] = knowledge_name
                page_article_content_arr = []
                page_article_content_arr.append("".join(page_article_content))
                question1["question_article_content"] = page_article_content_arr
                question1["question_article_content_translation"] = page_article_content_translation
                question1["question_article_id"] = article_id
                question1["question_audio_url"] = question_audio_url
                question1["question_audio_refer"] = response.meta["url"]
                question1["question_module_type"] = 6
                yield question1
        # 处理nano-content_in
        for content_in in question_cointainer_html.children(".nano-content_in").items():
            for question_html in content_in.children(".question").items():
                question2 = self.parse_question_html(question_html, response)
                question2["module"] = title_type
                question2["name"] = title_name
                question2["question_knowledge_name"] = knowledge_name
                page_article_content_arr = []
                page_article_content_arr.append("".join(page_article_content))
                question2["question_article_content"] = page_article_content_arr
                question2["question_article_content_translation"] = page_article_content_translation
                question2["question_article_id"] = article_id
                question2["question_audio_url"] = question_audio_url
                question2["question_audio_refer"] = response.meta["url"]
                question2["question_module_type"] = 6
                yield question2
            for item_html in content_in.children(".item").items():
                question_list = self.parse_item_html(item_html, response)
                for question3 in question_list:
                    question3["module"] = title_type
                    question3["name"] = title_name
                    question3["question_knowledge_name"] = knowledge_name
                    page_article_content_arr = []
                    page_article_content_arr.append("".join(page_article_content))
                    question3["question_article_content"] = page_article_content_arr
                    question3["question_article_content_translation"] = page_article_content_translation
                    question3["question_article_id"] = article_id
                    question3["question_audio_url"] = question_audio_url
                    question3["question_audio_refer"] = response.meta["url"]
                    question3["question_module_type"] = 6
                    yield question3

    def parse_question_html(self, question_html, response):
        question = QuestionItem()
        question_answer_content_str = ""
        question_content_str = []
        question_resolve_list = []
        question_content_file = []
        question_type = 0  # 1是选择，2判断,3是填空
        if question_html("input") is not None:
            input_class = question_html("input").attr("class")
            if input_class.index("fillBlankData") != -1:
                question_type = 3

        # 处理题干
        question_content_title = []
        """for question_content in question_html.children("p").items():
            if question_content.html() is not None:
                question_content_title.append(question_content.html())"""
        question_content_title.append("Complete the notes below.Write ONE WORD AND/OR A NUMBER for each answer.")

        # 处理填空题题型
        if question_type == 3:
            question_content = []

            is_fill_blank_page = False
            if question_html(".fillBlank_content").html() is not None:
                question_list = self.parse_fill_blank_data(question_html(".fillBlank_content "), response)
                question_content = question_list[0]
                question_content_file = question_list[1]
            else:
                question_content = self.parse_fill_blank_page_data(question_html(".drag_content"), response)
                is_fill_blank_page = True
            # 解析答案
            question_answer_container = question_html(".tea_explain_content")
            question_answer_temp = {}
            question_answer = {}
            for question_answer_html in question_answer_container(
                    ".exp_correct_answer_content .exp_correct_answer_desc ul").children("li").items():
                answer_num = question_answer_html(".pnum").text()[:-1]
                answer_text = question_answer_html(".answer").text()
                question_answer_temp[answer_num] = answer_text

            # 解析问题的解析
            question_resolve_list.append(question_answer_container(".exp_tea_explain_content .tea_explain_text").html())
            question_answer = question_answer_temp
            question_content_str.append("".join(question_content))
            question_answer_content_str = ",".join(list(question_answer.values()))
        question["question_order"] = list(question_answer.keys())[0]
        question["question_content"] = question_content_str
        question["question_answer"] = question_answer_content_str
        question["question_resolve_content"] = "".join(question_resolve_list)
        question["question_title"] = "".join(question_content_title)
        question["question_type"] = question_type
        question["question_content_file_url_list"] = question_content_file
        return question

    def parse_item_html(self, item_html, response):
        question_list = []
        question_type = item_html(".question .question_option .ops input").attr("class")
        if question_type is not None:
            if question_type.find("ielts_single_select") != -1:
                question_list.extend(self.parse_single_select_question(item_html, response))
            elif question_type.find("ielts_judgement_select") != -1:
                question_list.append(self.parse_judgement_question(item_html, response))
            elif question_type.find("ielts_multi_select ") != -1:
                question_list.append(self.parse_multi_select_question(item_html, response))
        elif item_html(".question table").attr("class").find("check_table") != -1:
            question_list.append(self.parse_table_question(item_html, response))
        return question_list

    def parse_judgement_question(self, item_html, response):
        question_content = []
        question_answer = []
        question_title = []
        for question_content_html in item_html(".question").children("p").items():
            if question_content_html.html() is not None:
                question_title.append("<p>" + question_content_html.html() + "</p>")
        for question_content_html in item_html(".question").children(".question_option").items():
            question_content.append("<p>" + str(question_content_html(".q_tit").text()) + "[BlankArea]" + "</p>")
        question_answer_container = item_html(".tea_explain_content")
        for question_answer_html in question_answer_container(
                ".exp_correct_answer_content .exp_correct_answer_desc ul").children().items():
            question_answer.append(question_answer_html("span").text())
        question_resolve = question_answer_container(".tea_explain_text").html()
        question = QuestionItem()
        question["question_title"] = question_title
        question_content_arr = []
        question_content_arr.append("".join(question_content))
        question["question_content"] = question_content_arr
        question["question_answer"] = ",".join(question_answer)
        question["question_resolve_content"] = question_resolve
        question["question_type"] = 2
        question["question_content_file_url_list"] = []
        return question

    def parse_single_select_question(self, item_html, response):
        question_content_list = []
        question_option_list = []
        question_answer_list = []
        question_resolve_list = []
        question_list = []
        for question_content_html in item_html(".question").children(".question_option").items():
            question_option_list_temp = []
            question_content_list.append(question_content_html(".q_tit ").text())
            for question_content_option in question_content_html.children(".ops").items():
                question_option_item = question_content_option("label").html();
                if question_option_item.find(".") != -1:
                    question_option_item = question_option_item[question_option_item.index(".") + 1:]
                question_option_list_temp.append(question_option_item)
            question_option_list.append(question_option_list_temp)
        question_answer_container = item_html(".tea_explain_content")
        question_answer_num = []
        for question_answer_html in question_answer_container(".exp_correct_answer_desc ul").children().items():
            question_answer_list.append(question_answer_html("span").text())
            question_answer_num_item = question_answer_html.text()
            if question_answer_num_item.find(".") != -1:
                question_answer_num_item = question_answer_num_item[:question_answer_num_item.index(".")]
            question_answer_num.append(question_answer_num_item)
        if question_answer_container(".tea_explain_text").children().html() is not None:
            for question_resolve_html in question_answer_container(".tea_explain_text").children("p").items():
                question_resolve_list.append(question_resolve_html.html())
        else:
            question_answer_html = question_answer_container(".tea_explain_text").text()
            question_resolve_list.append(question_answer_html)
        for i, value in enumerate(question_content_list):
            question = QuestionItem()
            question["question_title"] = value
            question["question_answer"] = question_answer_list[i]
            question["question_order"] = question_answer_num[i]
            print(value)
            if len(question_resolve_list) < len(question_content_list):
                question["question_resolve_content"] = "".join(question_resolve_list)
            else:
                question["question_resolve_content"] = question_resolve_list[i]
            question["question_content"] = question_option_list[i]
            question["question_type"] = 1
            question["question_content_file_url_list"] = []
            question_list.append(question)
        return question_list

    def parse_multi_select_question(self, item_html, response):
        question_option_list = []
        question_answer_list = []

        # 題目，选项
        question_content_html = item_html(".question").children(".question_option")
        question_title = question_content_html(".q_tit ").text()
        for question_content_option in question_content_html.children(".ops").items():
            question_item_ops = question_content_option("label").html();
            if question_item_ops.find(".") != -1:
                question_item_ops = question_item_ops[question_item_ops.index(".") + 1:]
            question_option_list.append(question_item_ops)

        # 答案、解析
        question_answer_container = item_html(".tea_explain_content")
        for question_answer_html in question_answer_container(".exp_correct_answer_desc ul").children().items():
            question_answer_list.append(question_answer_html("span").text())
        question_resolve_html = question_answer_container(".tea_explain_text").html()
        question = QuestionItem()
        question["question_title"] = question_title
        question["question_answer"] = "".join(question_answer_list)
        question["question_resolve_content"] = question_resolve_html
        question["question_content"] = question_option_list
        question["question_type"] = 4
        question["question_content_file_url_list"] = []
        return question

    # 处理表格摘要题，处理为填空题
    def parse_table_question(self, item_html, response):
        question_html = item_html(".question")
        question_title_list = []
        question_content_list = []
        question_answer_list = []
        for question_title in question_html.children("p").items():
            question_title_list.append("<p>" + question_title.html() + "</p>")
        for tr_index, table_tr in enumerate(question_html(".check_table").children("tr").items()):
            if tr_index > 0:
                for td_index, table_tr_td in enumerate(table_tr.children("td").items()):
                    if td_index == 0:
                        question_content_list.append("<p>" + table_tr_td.text() + "</p>")
        question_answer_container = item_html(".tea_explain_content")
        for answer_html in question_answer_container(
                ".exp_correct_answer_content .exp_correct_answer_desc ul").children("li").items():
            question_answer_list.append(answer_html(".answer").text())
        question_resolve_html = question_answer_container(".exp_tea_explain_content .tea_explain_text").html()
        question = QuestionItem()
        question['question_title'] = "".join(question_title_list)
        question['question_answer'] = ",".join(question_answer_list)
        questin_content_arr = []
        questin_content_arr.append("".join(question_content_list))
        question['question_content'] = questin_content_arr
        question['question_resolve_content'] = question_resolve_html
        question['question_type'] = 3
        question["question_content_file_url_list"] = []
        return question

    # 处理填空题
    def parse_fill_blank_data(self, blan_data_html, response):
        # print(blan_data_html)
        question_list = []
        question_content_list = []
        question_content_file = []
        for blank_content in blan_data_html.children().items():
            if blank_content.html() is not None:
                for question_img in blank_content.children("img").items():
                    question_content_file.append(question_img.attr("src"))
                blank_content_html = blank_content.html()
                input_pattern = re.compile(r'<input[^<]*?>')
                blank_content_html = re.sub(input_pattern, '[BlankArea]', blank_content_html)
                b_pattern = re.compile(r'<b[^<]*?</b>')
                blank_content_html = re.sub(b_pattern, '', blank_content_html)
                img_pattern = re.compile('<img[^>]*/>')
                blank_content_html = re.sub(img_pattern, '$img', blank_content_html)
                if blank_content_html.find("<tbody>") != -1:
                    question_content_list.append("<table>" + blank_content_html + "</table>")
                else:
                    question_content_list.append("<p>" + blank_content_html + "</p>")
        question_list.append(question_content_list)
        question_list.append(question_content_file)
        return question_list

    # 处理文章摘要，也就是填空题
    def parse_fill_blank_page_data(self, blan_data_html, response):
        question_list = []
        for div_content in blan_data_html.children("div").items():
            if div_content.html() is not None:
                if div_content.attr("class").strip() != "" and div_content.attr("class").find("drag_title") != -1:
                    question_list.append("<p>" + div_content.html() + "</p>")
                else:
                    for div_content_div in div_content.children("div").items():
                        question_list.append("<p>" + div_content_div.html() + "</p>")
        return question_list
