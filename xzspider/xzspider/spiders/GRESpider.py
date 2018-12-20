# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from xzspider.ItemSat import SatItem
from pyquery import PyQuery
import json
import re
import uuid


class SatSpider(scrapy.Spider):
    name = 'GreSpider'
    allowed_domains = ['smartstudy.com']
    start_urls = ['https://ti.smartstudy.com/api/textbook/question-packages?examinationId=3&subjectId=&pageSize=9',
                  'https://ti.smartstudy.com/api/textbook/question-packages?examinationId=3&textbookId=98&name=GRE官方150题&subjectId=&pageSize=9',
                  'https://ti.smartstudy.com/api/textbook/question-packages?examinationId=3&textbookId=11&name=GRE官方题库Issue&subjectId=&pageSize=9',
                  'https://ti.smartstudy.com/api/textbook/question-packages?examinationId=3&textbookId=12&name=GRE官方题库Argument&subjectId=& pageSize=9',
                  'https://ti.smartstudy.com/api/textbook/question-packages?examinationId=3&textbookId=93&name=GRE再要你命三千&subjectId=&pageSize=9']
    custom_settings = {
        'ITEM_PIPELINES': {'xzspider.GREpipelines.GREPipeline': 400, }
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
                if subjectName == "阅读":
                    module_type = 1
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_order"] = index
                            question["question_tag_name"] = question_tag_name
                            if questionId==4255:
                                print(questionId)
                            url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                            yield Request(url=url, meta={'question': question}, callback=self.parse_reading)

                elif subjectName == "数学":
                    module_type = 2
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_order"] = index
                            question["question_tag_name"] = question_tag_name
                            url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                            yield Request(url=url, meta={'question': question}, callback=self.parse_math)
                elif subjectName == "填空":
                    module_type = 3
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_order"] = index
                            question["question_tag_name"] = question_tag_name
                            url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                            yield Request(url=url, meta={'question': question}, callback=self.parse_math)
                elif subjectName == "写作":
                    module_type = 4
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_order"] = index
                            question["question_tag_name"] = question_tag_name
                            url = "https://ti.smartstudy.com/api/question/" + str(questionId)
                            yield Request(url=url, meta={'question': question},
                                          callback=self.parse_writing)
                elif subjectName == "单词":
                    module_type = 5
                    for practice in subjects["practiceList"]:
                        article_id = uuid.uuid1()
                        question_tag_name = practice["name"]
                        for index, questionId in enumerate(practice["questionIds"]):
                            question = SatItem()
                            question["module_name"] = module_name
                            question["module_type"] = module_type
                            question["article_id"] = article_id
                            question["question_order"] = index
                            question["question_tag_name"] = question_tag_name
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
        if json_str["code"] == 0:
            article_content = ""
            json_result = json_str["data"]["content"]
            if len(json_result["introduction"]["text"]):
                article_content += json_result["introduction"]["text"][0]["raw"]
            article_content += json_result["material"]["text"][0]["raw"]
            question_detail = json_result["question_detail"][0]
            question = self.parse_question_detail(question_detail, question)
            question["article_content"] = article_content
            question_knowledge = json_str["data"]["tagName"]
            question["question_knowledge"] = question_knowledge
            yield question

    def parse_fillblank(self, response):
        question = response.meta["question"]
        json_str = json.loads(response.body)
        if json_str["code"] == 0:
            json_result = json_str["data"]["content"]
            question_detail = json_result["question_detail"][0]
            question = self.parse_question_detail(question_detail, question)
            question_knowledge = json_str["data"]["tagName"]
            question["question_knowledge"] = question_knowledge
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

        question["question_title"] = question_content
        question["question_option"] = question_option
        question["question_content_file"] = question_content_files
        question["question_answer"] = question_answer
        question["question_resolve"] = question_analysis
        question["question_type"] = question_type
        return question
