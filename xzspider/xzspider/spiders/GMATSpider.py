# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from xzspider.ItemSat import SatItem
from pyquery import PyQuery
import json
import http.client
import re
import uuid


class GmatSpider(scrapy.Spider):
    name = 'GmatSpider'
    allowed_domains = ['smartstudy.com']
    start_urls = ['https://ti.smartstudy.com/api/textbook/question-packages?examinationId=5&textbookId=7',
                  'https://ti.smartstudy.com/api/textbook/question-packages?examinationId=5&textbookId=13',
                  'https://ti.smartstudy.com/api/textbook/question-packages?examinationId=5&textbookId=82',
                  'https://ti.smartstudy.com/api/textbook/question-packages?examinationId=5&textbookId=94'
                  ]
    custom_settings = {
        'ITEM_PIPELINES': {'xzspider.GMATpipelines.GMATPipeline': 300, }
    }
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
              'Referer': 'https://www.smartstudy.com'}

    def parse(self, response):
        json_str = json.loads(response.body)
        if json_str["code"] == 0:
            for item in json_str["data"]["questionPackageList"]["list"]:
                url = "https://ti.smartstudy.com/api/question-package/" + str(item["qpId"])
                print(item["qpId"])
                print(item["name"])
                yield Request(url=url, callback=self.parse_module)

    def parse_module(self, response):
        json_result = json.loads(response.body.decode("utf-8"))
        if json_result["code"] == 0:
            result_data = json_result["data"]
            module_name = result_data["name"]
            subjects_list = result_data["subjects"]
            for subjects in subjects_list:
                subjectName = subjects["subjectName"]
                module_type = 1
                if subjectName == "数学":
                    module_type = 1
                    count = 0
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            count = count + 1
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_tag_name"] = question_tag_name
                            question["question_order"] = index
                            url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                            yield Request(url=url, meta={'question': question}, callback=self.parse_math)
                elif subjectName == "语法(SC)":
                    module_type = 2
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_tag_name"] = question_tag_name
                            question["question_order"] = index
                            url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                            yield Request(url=url, meta={'question': question}, callback=self.parse_math)
                elif subjectName == "逻辑(CR)":
                    module_type = 3
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_tag_name"] = question_tag_name
                            question["question_order"] = index
                            url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                            yield Request(url=url, meta={'question': question}, callback=self.parse_math)
                elif subjectName == "阅读(RC)":
                    module_type = 4
                    if subjects.__contains__("practiceList"):
                        for practice in subjects["practiceList"]:
                            article_id = uuid.uuid1()
                            question_tag_name = practice["name"]
                            for index, questionId in enumerate(practice["questionIds"]):
                                question = SatItem()
                                question["module_name"] = module_name
                                question["module_type"] = module_type
                                question["article_id"] = article_id
                                question["question_tag_name"] = question_tag_name
                                question["question_order"] = index
                                url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                                yield Request(url=url, meta={'question': question}, callback=self.parse_reading)
                elif subjectName == "综合推理(IR)":
                    module_type = 5
                    if subjects.__contains__("practiceList"):
                        for practice in subjects["practiceList"]:
                            article_id = uuid.uuid1()
                            question_tag_name = practice["name"]
                            for index, questionId in enumerate(practice["questionIds"]):
                                question = SatItem()
                                question["module_name"] = module_name
                                question["module_type"] = module_type
                                question["article_id"] = article_id
                                question["question_tag_name"] = question_tag_name
                                question["question_order"] = index
                                url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                                yield Request(url=url, meta={'question': question}, callback=self.parse_multiple)
                elif subjectName == "写作":
                    module_type = 6
                    if subjects.__contains__("practiceList"):
                        for practice in subjects["practiceList"]:
                            article_id = uuid.uuid1()
                            question_tag_name = practice["name"]
                            for index, questionId in enumerate(practice["questionIds"]):
                                question = SatItem()
                                question["module_name"] = module_name
                                question["module_type"] = module_type
                                question["article_id"] = article_id
                                question["question_order"] = index
                                url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                                yield Request(url=url,
                                              meta={'question': question, 'question_knowledge': question_tag_name},
                                              callback=self.parse_writing)
                elif subjectName == "单词":
                    module_type = 7
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_tag_name"] = question_tag_name
                            question["question_order"] = index
                            url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                            yield Request(url=url, meta={'question': question}, callback=self.parse_word)

    def parse_reading(self, response):
        question = response.meta["question"]
        json_str = json.loads(response.body)
        if json_str["code"] == 0:
            json_result = json_str["data"]["content"]
            question_knowledge = json_str["data"]["tagName"]
            article_content = json_result["material"]["text"][0]["raw"]
            question_detail = json_result["question_detail"][0]
            question = self.parse_question_detail(question_detail, question)
            question["article_content"] = article_content
            question["question_knowledge"] = question_knowledge
            question["question_tag_name"] = json_str["data"]["name"]
            yield question

    def parse_math(self, response):
        question = response.meta["question"]
        json_str = json.loads(response.body)
        if json_str["code"] == 0:
            json_result = json_str["data"]["content"]
            question_detail = json_result["question_detail"][0]
            question = self.parse_question_detail(question_detail, question)
            question_knowledge = json_str["data"]["tagName"]
            question["question_knowledge"] = question_knowledge
            yield question

    def parse_multiple(self, response):
        question = response.meta["question"]
        json_str = json.loads(response.body)
        if json_str["code"] == 0:
            json_result = json_str["data"]["content"]
            question_knowledge = json_str["data"]["tagName"]
            article_content = json_result["material"]["text"][0]["raw"]
            if json_result["material"].__contains__("picture") and json_result["material"]["picture"] != "":
                img_url = "https://media8.smartstudy.com/"
                img_url += json_result["material"]["picture"]
                question["article_content_file"] = img_url
            question["article_content"] = article_content
            question["question_knowledge"] = question_knowledge
            question["question_tag_name"] = json_str["data"]["name"]
            question_detail = json_result["question_detail"]
            question_list = []
            for index, question_item in enumerate(question_detail):
                question_item_new = SatItem()
                question_item_new["module_name"] = question["module_name"]
                question_item_new["module_type"] = question["module_type"]
                question_item_new["article_id"] = question["article_id"]
                question_item_new["question_order"] = index
                question_item_new["article_content"] = article_content
                question_item_new["question_knowledge"] = question_knowledge
                question_item_new["question_tag_name"] = json_str["data"]["name"]
                question_item_new = self.parse_question_detail(question_item, question_item_new)
                question_list.append(question_item_new)
            question["question_list"] = question_list
            yield question

    def parse_word(self, response):
        question = response.meta["question"]
        json_str = json.loads(response.body)
        if json_str["code"] == 0:
            json_result = json_str["data"]["content"]
            question_detail = json_result["question_detail"][0]
            question = self.parse_question_detail(question_detail, question)
            question_knowledge = json_str["data"]["tagName"]
            question["question_knowledge"] = question_knowledge
            yield question

    def parse_writing(self, response):
        question = response.meta["question"]
        json_str = json.loads(response.body)
        question_knowledge = response.meta["question_knowledge"]
        if json_str["code"] == 0:
            article_content = ""
            json_result = json_str["data"]["content"]
            if len(json_result["introduction"]["text"]):
                article_content += json_result["introduction"]["text"][0]["raw"]
            if len(json_result["material"]["text"]) > 0:
                article_content += json_result["material"]["text"][0]["raw"]
            question_detail = json_result["question_detail"][0]
            question = self.parse_question_detail(question_detail, question)
            question["article_content"] = article_content
            question["question_knowledge"] = question_knowledge
            question["question_tag_name"] = json_str["data"]["name"]
            yield question

    def parse_question_detail(self, question_detail, question):
        question_type = question_detail["question_type"]
        question_content = question_detail["question"]["text"][0]["raw"]
        question_picture = ""
        if question_detail["question"].__contains__("picture"):
            question_picture = question_detail["question"]["picture"]
        question_content_files = []
        question_analysis = ""
        img_url = "https://media8.smartstudy.com/"
        if question_picture is not None and question_picture != '':
            question_content_files.append(img_url + question_picture)
            question_content = "<p>$img</p>" + question_content
        elif question_content.find("<img") != -1:
            img_pattern = re.compile('<img[^>]*/>')
            img_list = re.findall(img_pattern, question_content)
            for img in img_list:
                img_src = PyQuery(img).attr("src")
                question_content_files.append("https:" + img_src)
            question_content = re.sub(img_pattern, '$img', question_content)
        if question_detail["answer_analysis"]["text"] is not None and len(
                question_detail["answer_analysis"]["text"]) > 0:
            question_analysis = question_detail["answer_analysis"]["text"][0]["raw"]
        question_option = []
        question_answer = question_detail["answer"]
        if question_type == 1:
            for choice in question_detail["choices"]:
                question_option.append(choice)
            item_char = 'A'
            question_answer = chr(ord(item_char) + question_answer)
        elif question_type == 2:
            question_answer_temp = [];
            for choice in question_detail["choices"]:
                question_option.append(choice)
            for answer in question_detail["answer"]:
                item_char = 'A'
                question_answer_temp.append(chr(ord(item_char) + answer))
            question_answer = " ".join(question_answer_temp)
        elif question_type == 3:
            question_option_temp = []
            input_pattern = re.compile(r'<input[^<]*?>')
            question_content = re.sub(input_pattern, '[BlankArea]', question_content)
            for choice in question_detail["choices"]:
                answer_index = choice["question_index"]
                answer_content = []
                for content in choice["content"]:
                    answer_content.append(content)
                question_option_temp.append("/".join(answer_content))
            question_option.append(",".join(question_option_temp))
            question_answer = ",".join(question_option_temp)
        elif question_type == 4:
            print(question_type)

        question["question_title"] = question_content
        question["question_option"] = question_option
        question["question_content_file"] = question_content_files
        question["question_answer"] = question_answer
        question["question_resolve"] = question_analysis
        question["question_type"] = question_type
        return question
