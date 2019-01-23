# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DianpingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class RegionItem(scrapy.Item):
    # define the fields for your item here like:
    sort = scrapy.Field()
    city = scrapy.Field()
    region = scrapy.Field()
    region_sub = scrapy.Field()
    url = scrapy.Field()
    pass

    
class ShopItem(scrapy.Item):
    # define the fields for your item here like:
    sort = scrapy.Field()
    shop_id = scrapy.Field()
    name = scrapy.Field()
    full_name = scrapy.Field()
    url = scrapy.Field()
    city = scrapy.Field()
    city_en_name = scrapy.Field()
    city_id = scrapy.Field()
    region = scrapy.Field()
    region_sub = scrapy.Field()
    address = scrapy.Field()
    shop_lat = scrapy.Field()
    shop_lng = scrapy.Field()
    city_lat = scrapy.Field()
    city_lng = scrapy.Field()
    power = scrapy.Field()
    shop_power = scrapy.Field()
    # 567条评论
    vote_total = scrapy.Field()
    shop_type = scrapy.Field()
    shop_group_id = scrapy.Field()
    main_region_id = scrapy.Field()
    main_category_name = scrapy.Field()
    main_category_id = scrapy.Field()
    # food
    category_url_name = scrapy.Field()
    # 比如 美食
    category_name = scrapy.Field()
    phone = scrapy.Field()
    # 开放时间
    business_hours = scrapy.Field()
    # 人均
    avg_price = scrapy.Field()
    # 评分
    taste_score = scrapy.Field()
    service_score = scrapy.Field()
    env_score = scrapy.Field()
    # 是否关闭
    is_open = scrapy.Field()
    version = scrapy.Field()
