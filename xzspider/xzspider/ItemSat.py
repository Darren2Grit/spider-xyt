import scrapy


class SatItem(scrapy.Item):
    module_name = scrapy.Field()  # 所属模块名称
    module_type = scrapy.Field()  # 所属模块类型(1阅读，2数学，3语法，4写作)
    question_tag_name = scrapy.Field()  # 题目所属tag,文章标题
    article_id = scrapy.Field()  # 文章id
    article_content = scrapy.Field()  # 文章内容
    question_knowledge = scrapy.Field()  # 题目知识点
    question_title = scrapy.Field()  # 题目标题或者填空题的内容
    question_option = scrapy.Field()  # 题目选项
    question_answer = scrapy.Field()  # 题目答案
    question_resolve = scrapy.Field()  # 题目解析
    question_type = scrapy.Field()  # 題目類型(1选择 2多选 3填空 5 写作)
    question_order = scrapy.Field()  # 题目排序
    question_content_file = scrapy.Field()  # content_内容
