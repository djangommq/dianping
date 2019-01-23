import requests
from lxml import etree
import json
import re
import os

def get_css_html(url):
    res = requests.get(url)
    return res.text

def parse_svg(url):
    word_px = {}
    # 返回汉字和px的对照
    svg_content = requests.get(url).text
    # 先找出单个字的px
    font_size_re = r'(?<=font\-size\:)([0-9]*)(?=px)'
    font_size_str = re.findall(font_size_re, svg_content)[0]
    font_size = int(font_size_str)
    if font_size == 14:
        offset = 23
    elif font_size == 12:
        offset = 24
    else:
        print('新字符集', font_size)
        return 0
    # 匹配所有的字
    word_lines_re = r"""(<text\ x=[\"0-9\ ]*\ [^\s]*?)(?=</text>)"""
    word_lines = re.findall(word_lines_re, svg_content)
    # 选中效果
    # <text x="0" y="39">74160385768549328380773067769858036439278881591657
    # <text x="0" y="856">鼠炝情薄仔灵沂奉熬羊肥描朱酿糍塌冬虚杭陆燃冰锡幔左正鲻桐别公饺碎禹池丹顺宾熏柱条血都肴耳乓新蝴桂
    # 共有四种情况,数字+12px, 汉字+12px, 数字+14px, 汉字+14px, 
    for line in word_lines:
        y = int(line.split('y="')[1].split('">')[0])
        words = line.split('>')[1]
        test_word = words[0]
        try:
            s = int(test_word)
            # 不抛异常就是数字
            word_type = 'int'
        except:
            # 当前字符集是汉字
            word_type = 'str'
        # 如果是14px汉字
        if word_type == 'str' and font_size == 14:  
            y_px = y - offset
            for i in range(1, len(words)+1):
                word = words[i-1] 
                x_px = (i-1) * font_size
                px_str = '{' + "background:-{}.0px -{}.0px;".format(x_px, y_px) + '}'
                word_px[px_str] = word
        # 如果是14px数字
        elif word_type == 'int' and font_size == 14:  
            y_px = y - offset
            for i in range(1, len(words)+1):
                word = words[i-1]
                if int(word) == 1:
                    x_px = i * font_size - 7
                else: 
                    x_px = i * font_size - 6
                px_str = '{' + "background:-{}.0px -{}.0px;".format(x_px, y_px) + '}'
                word_px[px_str] = word
        # 如果是12px汉字
        elif word_type == 'str' and font_size == 12:  
            y_px = y - offset
            for i in range(1, len(words)+1):
                word = words[i-1] 
                x_px = (i-1) * font_size
                px_str = '{' + "background:-{}.0px -{}.0px;".format(x_px, y_px) + '}'
                word_px[px_str] = word
        # 如果是12px数字
        elif word_type == 'int' and font_size == 12:  
            y_px = y - offset
            for i in range(1, len(words)+1):
                word = words[i-1]
                if int(word) == 1:
                    x_px = i * font_size - 6
                else: 
                    x_px = i * font_size - 5
                px_str = '{' + "background:-{}.0px -{}.0px;".format(x_px, y_px) + '}'
                word_px[px_str] = word
    return word_px

def get_css_text_info(css_url, text_css_version):
    # 请求到css内容
    css_html = get_css_html(css_url)
    url_pattern = r'//[^\s]*.svg'
    urls = re.findall(url_pattern, css_html)
    print(urls)
    px_word_dict = {}
    for url in urls:
        url = 'http:' + url
        # 获取每个svg图片
        print(url)
        px_word_dict.update(parse_svg(url))
    # 类名和px对照
    # kn4to{background:-204.0px -287.0px;}
    class_pxs = re.findall(r'[a-z0-9]{5}\{[a-z0-9\:\-\.\s\;]*\}', css_html)
    # 换算成字典:
    px_class_dict = {}
    for class_px in class_pxs:
        class_str = class_px[0:5]
        px_str = class_px[5:]
        px_class_dict[px_str] = class_str
    
    class_word_dict = {}
    # 合并后保存
    for px, class_str in px_class_dict.items():
        class_word_dict[class_str] = px_word_dict.get(px)
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), './text_css_version/{}.json'.format(text_css_version))
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(class_word_dict))
    print(class_word_dict)
    return class_word_dict


if __name__ == '__main__':
    css_url = 'http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/3ae476a41ae3b7735e549501a879ce85.css'
    get_css_text_info(css_url, 'test')

    # parse_svg('ss')
