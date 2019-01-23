import time
import os
import sys

model_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], '../../')
sys.path.append(model_dir)

from dianping.utils.mongodb_utils import get_db
from dianping.utils import load_cities, load_shops


if __name__ == "__main__":
    format = '%Y-%m-%d-%H-%M-%S'
    current = time.localtime(time.time())
    dt = time.strftime(format, current)
    statistics_path = './progress_info.txt'
    cities = load_cities()
    with open(statistics_path, 'a', encoding='utf-8') as f:
        f.writelines('{}, 目前进展如下:\n'.format(dt))
        print('{}, 目前进展如下:'.format(dt))
        f.writelines('商店总数:{}\n'.format(load_shops().count()))
        print('商店总数:{}'.format(load_shops().count()))
        for city in cities:
            city_name = city.get('name')
            query1 = {
                'city': city_name,
            }
            query2 = {
                'city': city_name,
                'version': {
                    '$exists': True,
                },
            }
            f.writelines('{}的商店总数:{}, \t请求详情进度:{}\n'.format(city_name, load_shops(query1).count(), load_shops(query2).count()))
            print('{}的商店总数:{}, \t请求详情进度:{}'.format(city_name, load_shops(query1).count(), load_shops(query2).count()))
