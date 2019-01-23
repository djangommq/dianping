# -*- coding: utf-8 -*-
# 获取城市-区-地区url
import scrapy
from dianping.utils import load_cities
from lxml import etree
from dianping.items import RegionItem


class RegionSpider(scrapy.Spider):
    name = 'region'
    allowed_domains = ['dianping.com']
    # start_urls = ['http://dianping.com/']

    def __init__(self, city=None):
        # 默认运行北京
        self.city = city

    def start_requests(self):
        if self.city is None:
            cities = load_cities()
            for city in cities:
                url = 'http://www.dianping.com/{}/ch10'.format(city.get('ename'))
                request = scrapy.Request(url, callback=self.parse_region, dont_filter=True)
                request.meta['origin_url'] = url
                yield request
        else:
            cities = load_cities()
            for city in cities:
                if city.get('name') == self.city:
                    url = 'http://www.dianping.com/{}/ch10'.format(city.get('ename'))
                    request = scrapy.Request(url, callback=self.parse_region, dont_filter=True)
                    request.meta['origin_url'] = url
                    yield request

    def parse_region(self, response):
        # 判断出现验证码的情况
        new_url = response.url
        if new_url.startswith('https://verify.meituan.com/'):
            # 表示需要重试url
            print('有验证码, 重试')
            url = response.meta['origin_url'] 
            print('出现验证码重试的url：{}'.format(url))
            request = scrapy.Request(url, callback=self.parse_region, dont_filter=True)
            request.meta['origin_url'] = url
            yield request
        else:    
            # 找出区一级的url
            region_xpath = '//*[@id="region-nav"]//a'
            page_source = etree.HTML(response.text)
            a_tags = page_source.xpath(region_xpath)
            for tag in a_tags:
                if tag.xpath('./@data-cat-id') == []:
                    print(tag.xpath('./@href'))
                    continue
                region_url = tag.xpath('./@href')[0]
                request = scrapy.Request(region_url, callback=self.parse_region_sub, dont_filter=True)
                request.meta['origin_url'] = region_url
                yield request
    
    def parse_region_sub(self, response):

        # 判断验证码
        new_url = response.url
        if new_url.startswith('https://verify.meituan.com/'):
            # 表示需要重试url
            print('有验证码, 重试')
            region_url = response.meta['origin_url'] 
            print('出现验证码重试的url：{}'.format(region_url))
            request = scrapy.Request(region_url, callback=self.parse_region_sub, dont_filter=True)
            request.meta['origin_url'] = region_url
            yield request
        else:
            region_sub_xpath = '//*[@id="region-nav-sub"]//a'
            page_source = etree.HTML(response.text)
            a_tags = page_source.xpath(region_sub_xpath)
            region = page_source.xpath('//*[@id="region-nav"]/a[@class="cur"]/span/text()')[0]
            city = page_source.xpath('//*[@id="logo-input"]/div/a[2]/span[2]/text()')[0]
            for tag in a_tags:
                if tag.xpath('./@data-cat-id') == []:
                    print(tag.xpath('./@href')[0])
                    continue
                item = RegionItem()
                item['sort'] = 'region'
                item['city'] = city
                item['region'] = region
                item['region_sub'] = tag.xpath('./span/text()')[0]
                item['url'] = tag.xpath('./@href')[0]
                yield item




