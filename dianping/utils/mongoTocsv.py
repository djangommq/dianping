import os
import csv
from dianping.utils import get_db

# 获取链接数据库的对象
mongo_client=get_db()
shop_fields=[
      'sort',
      'version',
      'url',
      'full_name',
      'city_en_name',
      'address',
      'city_id',
      'shop_lat',
      'shop_lng',
      'city_lat',
      'city_lng',
      'power',
      'shop_power',
      'shop_type',
      'shop_group_id',
      'main_region_id',
      'main_category_name',
      'main_category_id',
      'category_url_name',
      'category_name',
      'vote_total',
      'is_open',
      'phone',
      'business_hours',
      'avg_price',
      'taste_score',
      'service_score',
      'env_score',
]

if __name__ == '__main__':
    info_list=mongo_client.all_items('shop')
    filepath=os.path.join(os.path.dirname(__file__),'../output_data')
    if os.path.exists(filepath):
          os.makedirs(filepath)
    filename=os.path.join(filepath,'shop.csv')

    with open(filename,'a',encoding='utf-8',newline='')as f:
          writer=csv.DictWriter(f,fieldnames=shop_fields)
          if not os.path.getsize(filename):
                writer.writeheader()
          for info in info_list:
              writer.writerow(info)

    print('数据成功导出!')