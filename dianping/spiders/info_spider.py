# -*- coding: utf-8 -*-
import scrapy
from dianping.utils import load_cities, load_regions, load_shops, parse_text_svg
from lxml import etree
from dianping.items import RegionItem, ShopItem
import demjson
import traceback
from dianping.utils import load_text_css
from dianping.utils.parse_css_text import get_css_text_info

# 使用selenium解析经纬度信息
from selenium import webdriver


class InfoSpider(scrapy.Spider):
    name = 'info'
    allowed_domains = ['dianping.com']
    # start_urls = ['http://dianping.com/']
    
    def __init__(self, city='北京', group=None):
        # 默认运行北京
        self.city = city
        self.group = group

    def start_requests(self):
        # address 没有表示还没请求详情
        while True:
            query = {
                'city': self.city,
                'version': {
                    '$exists': False,
                    },
            }
            shops = load_shops(query)
            if shops is None:
                break
            else:
                for shop in shops:
                    url = shop.get('url')
                    if self.group is not None and url.endswith(self.group):
                        request = scrapy.Request(url, callback=self.parse_info, dont_filter=True)
                        request.meta['origin_shop'] = shop
                        yield request
                    

    def parse_info(self, response):
        origin_shop = response.meta['origin_shop']
        
        # 判断是否弹出验证码
        new_url = response.url
        if new_url.startswith('https://verify.meituan.com/'):
            # 表示需要重试url
            print('有验证码, 重试')
            url = origin_shop.get('url')
            print('出现验证码重试的url：{}'.format(url))
            request = scrapy.Request(url, callback=self.parse_info, dont_filter=True)
            request.meta['origin_shop'] = origin_shop
            yield request
        else:
            # 使用selenium解析经纬度信息
            url = origin_shop.get('url')
            while True:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                chrome = webdriver.Chrome(chrome_options=options)
                chrome.get(url)

                e = etree.HTML(chrome.page_source)
                try:
                    img_src = e.xpath('//div[@id="map"]/img/@src')[0]
                    lat_lng_str = img_src.split('|')[1]
                    lat_lng_list = lat_lng_str.split(',')
                    lat = lat_lng_list[0]
                    lng = lat_lng_list[1]
                    chrome.quit()
                except:
                    lat = ''
                    lng = ''
                    chrome.quit()
                if lat!=''and lng!='':
                    break

            page_source = etree.HTML(response.text)

            # 解析出原始信息
            shop_info_xpath = '//script[10]'
            try:
                shop_info_tag = page_source.xpath(shop_info_xpath)[0]
            except:
                # 有的页面是另一种
                shop_info_tag = page_source.xpath('//*[@id="top"]/script[1]')[0]

            try:
                shop_info_dict = demjson.decode(shop_info_tag.xpath('./text()')[0].split('shop_config=')[1])

                # 解析商家的id
                item = ShopItem()
                # 加入url作为去重的标准
                item['sort'] = 'shop'
                # 控制数据的版本
                item['version'] = '0'
                item['url'] = origin_shop.get('url')

                item['full_name'] = shop_info_dict.get('fullName')
                item['city_en_name'] = shop_info_dict.get('cityEnName')
                item['address'] = shop_info_dict.get('address')
                item['city_id'] = shop_info_dict.get('cityId')
                # item['shop_lat'] = shop_info_dict.get('shopGlat')
                # item['shop_lng'] = shop_info_dict.get('shopGlng')
                item['shop_lat'] = lat
                item['shop_lng'] = lng
                item['city_lat'] = shop_info_dict.get('cityGlat')
                item['city_lng'] = shop_info_dict.get('cityGlng')
                item['power'] = shop_info_dict.get('power')
                item['shop_power'] = shop_info_dict.get('shopPower')
                item['shop_type'] = shop_info_dict.get('shopType')
                item['shop_group_id'] = shop_info_dict.get('shopGroupId')
                item['main_region_id'] = shop_info_dict.get('mainRegionId')
                item['main_category_name'] = shop_info_dict.get('mainCategoryName')
                item['main_category_id'] = shop_info_dict.get('mainCategoryId')
                # food
                item['category_url_name'] = shop_info_dict.get('categoryURLName')
                # 比如 美食
                item['category_name'] = shop_info_dict.get('categoryName')

                # 有一个textCssVersion, 应该是会定期更新文字库
                # 支持自动更新字库
                text_css_version = shop_info_dict.get('textCssVersion')
                # 加载一下字库看行不行
                text_css_info = load_text_css(text_css_version)
                if text_css_info is None:
                    print('网站的字符集有变更, 需要重新解析css')
                    # 抽取css的url
                    css_xpath = '//link[contains(@rel,"stylesheet") and contains(@href, "svgtextcss")]/@href'
                    css_url = 'http:' + page_source.xpath(css_xpath)[0]
                    get_css_text_info(css_url, text_css_version)

                # 解析svg字体
                vote_xpath = '//*[@id="reviewCount"]'
                item['vote_total'] = parse_text_svg(vote_xpath, page_source,text_css_version)

                # 如果店铺已关闭, 则营业时间和电话都没有了
                shop_closed_xpath = '//p[@class="shop-closed"]'
                shop_closed_tag = page_source.xpath(shop_closed_xpath)
                if shop_closed_tag != []:
                    # 店铺已关闭
                    item['is_open'] = False
                else:
                    item['is_open'] = True
                    phone_xpath = '//*[@id="basic-info"]/p'
                    item['phone'] = parse_text_svg(phone_xpath, page_source,text_css_version)

                    # 开放时间
                    bh_xpath = '//*[@id="basic-info"]/div[4]/p[1]/span[2]'
                    item['business_hours'] = parse_text_svg(bh_xpath, page_source,text_css_version)

                # 人均
                avg_xpath = '//*[@id="avgPriceTitle"]'
                item['avg_price'] = parse_text_svg(avg_xpath, page_source,text_css_version)
                # 评分
                taste_xpath = '//*[@id="comment_score"]/span[1]'
                item['taste_score'] = parse_text_svg(taste_xpath, page_source,text_css_version)
                service_xpath = '//*[@id="comment_score"]/span[2]'
                item['service_score'] = parse_text_svg(service_xpath, page_source,text_css_version)
                env_xpath = '//*[@id="comment_score"]/span[3]'
                item['env_score'] = parse_text_svg(env_xpath, page_source,text_css_version)
                # print(item)
                yield item
            except Exception as e:
                # print(item)
                print(traceback.format_exc(), e)
                print('静态信息解析错误, 查看原因.')





