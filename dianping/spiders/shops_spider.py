# -*- coding: utf-8 -*-
# 获取每一个地区餐馆的url列表
import scrapy
from dianping.utils import load_cities, load_regions
from lxml import etree
from dianping.items import RegionItem, ShopItem


class ShopsSpider(scrapy.Spider):
    name = 'shops'
    allowed_domains = ['dianping.com']
    # start_urls = ['http://dianping.com/']
    
    def __init__(self, city='北京'):
        # 默认运行北京
        self.city = city

    def start_requests(self):
        query_region = {
            'city': self.city,
        }
        regions = load_regions(query_region)
        for region in regions:
            url = region.get('url')
            request = scrapy.Request(url, callback=self.parse_pages, dont_filter=True)
            request.meta['region'] = region
            request.meta['origin_url'] = url
            yield request

    def parse_pages(self, response):
        region = response.meta['region']
        
        # 判断是否弹出验证码
        new_url = response.url
        if new_url.startswith('https://verify.meituan.com/'):
            # 表示需要重试url
            print('有验证码, 重试')
            url = response.meta['origin_url']
            if '?' in url:
                url = url.split('?')[0] 
            print('出现验证码重试的url：{}'.format(url))
            request = scrapy.Request(url, callback=self.parse_pages, dont_filter=True)
            request.meta['region'] = region
            request.meta['origin_url'] = url
            yield request
        else:
            page_source = etree.HTML(response.text)
            shop_list_xpath = '//*[@id="shop-all-list"]/ul/li'
            shop_lists_tag = page_source.xpath(shop_list_xpath)
            # 解析商家的id
            for tag in shop_lists_tag:
                item = ShopItem()
                item['sort'] = 'shop'
                a_tag = tag.xpath('./div[1]/a')[0]
                item['shop_id'] = a_tag.xpath('./@data-shopid')[0]
                item['url'] = a_tag.xpath('./@href')[0]
                item['name'] = tag.xpath('./div[2]/div[1]/a/h4/text()')[0]
                item['region'] = region.get('region')
                item['region_sub'] = region.get('region_sub')
                item['city'] = region.get('city')
                yield item

            # 直接访问下一页
            next_page_xpath = '//a[@title="下一页"]'
            next_page_tag = page_source.xpath(next_page_xpath)
            if next_page_tag != []:
                next_page_url = next_page_tag[0].xpath('./@href')[0]
                if '?' in next_page_url:
                    next_page_url = next_page_url.split('?')[0] 
                request = scrapy.Request(next_page_url, callback=self.parse_pages, dont_filter=True)
                request.meta['region'] = region
                request.meta['origin_url'] = next_page_url
                yield request
            else:
                print('结束')





