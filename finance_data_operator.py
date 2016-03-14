import json
import datetime


class FinanceDataOperator(object):
    def __init__(self, resource_name, map_name):
        with open(resource_name, 'r') as f:
            self.resources = json.load(f)['list']['resources']
        with open(map_name, 'r') as f:
            self.maps = json.load(f)

    def get_time(self):
        raw_time = self.resources[0]['resource']['fields']['utctime']
        raw_time = raw_time.split('T')[0]
        time_list = [int(i) for i in raw_time.split('-')]
        days = datetime.datetime(time_list[0], time_list[1], time_list[2])
        return days

    def days_til_now(self):
        return (datetime.datetime.now() - self.get_time()).days

    def get_rate(self, name):
        def contain_chinese(check_str):
            return all(u'\u4e00' <= char <= u'\u9fff' for char in check_str)

        if name is None:
            return
        elif contain_chinese(name):
            maps = self.maps['chinese_to_code']
            return self.get_rate(maps.get(name))
        else:
            name = name.upper()
            if name == 'USD':
                return 1.0
            resources = self.resources
            for resource in resources:
                r = resource['resource']
                if r['fields']['name'] == 'USD/' + name:
                    return float(r['fields']['price'])

    def trans_currency(self, from_, to, amount, accuracy=3):
        from_rate = self.get_rate(from_)
        to_rate = self.get_rate(to)
        price = amount / from_rate * to_rate
        result = {}
        result['price'] = round(price, accuracy)
        result['from'] = from_
        result['to'] = to
        return result
