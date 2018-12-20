# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WritingItem(scrapy.Item):
    name = scrapy.Field()
    question_title = scrapy.Field()  # 问题名称
    question_knowledge_name = scrapy.Field()  # 问题的知识点名称
    question_answer = scrapy.Field()  # 问题的答案
    question_content = scrapy.Field()  # 问题的题干
    question_type = scrapy.Field()  # 问题的类型
    question_resolve_content = scrapy.Field()  # 问题的解析
    question_article_id = scrapy.Field()  # 题目原文id
    question_article_content = scrapy.Field()  # 题目原文
    question_article_content_file = scrapy.Field()  # 题目原文中的文件
    question_audio_content = scrapy.Field()  # 题目听力原文
    question_audio_url = scrapy.Field()  #
    question_audio_refer = scrapy.Field()
    question_module_type=scrapy.Field()
