import time
import os
import sys

model_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], '../../')
sys.path.append(model_dir)

from dianping.utils.mongodb_utils import get_db
from dianping.utils import load_cities, load_regions


if __name__ == "__main__":
    format = '%Y-%m-%d-%H-%M-%S'
    current = time.localtime(time.time())
    dt = time.strftime(format, current)
    statistics_path = './progress_info.txt'
    cities = load_cities()
    with open(statistics_path, 'a', encoding='utf-8') as f:
        f.writelines('{}, 目前进展如下:\n'.format(dt))
        print('{}, 目前进展如下:'.format(dt))
        f.writelines('地区总数:{}\n'.format(load_regions().count()))
        print('地区总数:{}'.format(load_regions().count()))
        for city in cities:
            city_name = city.get('name')
            query = {
                'city': city_name,
            }
            f.writelines('{}的地区总数:{}\n'.format(city_name, load_regions(query).count()))
            print('{}的地区总数:{}'.format(city_name, load_regions(query).count()))
