import os
import sys
import csv

model_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], '../../')
sys.path.append(model_dir)
from dianping.utils.mongodb_utils import get_db
import json

def load_cities():
    cities_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../input_data/cities.txt')
    cities = []
    city_field = [
        'name',
        'ename'
    ]
    with open(cities_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f, fieldnames=city_field)
        for row in csv_reader:
            if csv_reader.line_num == 1:
                continue
            cities.append(dict(row))
    return cities

def load_regions(query=None):
    db = get_db()
    rs = db.find('region', query)
    return rs
    
# 用于加载多个餐厅
def load_shops(query=None):
    db = get_db()
    rs = db.find('shop', query)
    return rs

# 用于加载单个餐厅
def load_shop(query=None):
    db = get_db()
    rs = db.find_one('shop', query)
    return rs

# 加载字符表
def load_text_css(text_css_version):
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), './text_css_version/{}.json'.format(text_css_version))

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            s = f.read()
            result = json.loads(s)
        return result
    except:
        return None


# 定义一个方法, 根据xpath自动组合成一个字符串, 仅适用于大众点评
def parse_text_svg(xpath, page_source, text_css_version):
    css_text_dict = load_text_css(text_css_version)
    tags = page_source.xpath(xpath)[0].xpath('.//*/@class|./text()')
    result = ''
    for tag in tags:
        if tag == 'info-name':
            continue
        temp = css_text_dict.get(tag)
        if temp is None:
            # 表示是原文, 否则就是svg取字
            result += tag
        else:
            result += temp
    return result.strip()

