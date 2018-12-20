# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QuestionItem(scrapy.Item):
    module = scrapy.Field()  # 所属模块
    name = scrapy.Field()  # 所属模块具体名称
    question_title = scrapy.Field()  # 问题标题
    question_knowledge_name = scrapy.Field()  # 问题的知识点名称
    question_answer = scrapy.Field()  # 问题的答案
    question_content = scrapy.Field()  # 问题的内容以及选项
    question_module_type = scrapy.Field()  # 问题的类型
    question_type = scrapy.Field()  # 问题所属模块(1托福阅读)（1 选择，2判断，3填空 4多选,6插入题）
    question_resolve_content = scrapy.Field()  # 问题的解析
    question_belong_paragraph = scrapy.Field()  # 问题所属自然段
    question_article_title = scrapy.Field()  # 问题的文章标题
    question_article_id = scrapy.Field()  # 问题的id
    question_article_content = scrapy.Field()  # 问题的文章
    question_article_content_translation = scrapy.Field()  # 问题文章的翻译
    question_audio_url = scrapy.Field()
    question_audio_article_content = scrapy.Field()  # 听力原文
    question_content_file_url_list = scrapy.Field()  # 问题图片url
    question_audio_refer = scrapy.Field()  # 资源图片的来源
    question_insert_content=scrapy.Field()
    question_order = scrapy.Field()
