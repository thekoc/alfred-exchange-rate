import json
import datetime


class FinanceDataOperator(object):
    def __init__(self, resource_name, map_name):
        with open(resource_name, 'r') as f:
            self.resources = json.load(f)['list']['resources']
        with open(map_name, 'r') as f:
            self.maps = json.load(f)

    def __get_currency_from_name(self, country):
        return self.maps['name_to_currency'].get(country)

    def __get_currency_from_code(self, country):
        return self.maps['code_to_currency'].get(country)

    def get_time(self):
        raw_time = self.resources[0]['resource']['fields']['utctime']
        raw_time = raw_time.split('T')[0]
        time_list = [int(i) for i in raw_time.split('-')]
        days = datetime.datetime(time_list[0], time_list[1], time_list[2])
        return days

    def days_til_now(self):
        return (datetime.datetime.now() - self.get_time()).days

    def get_multifunctional(self, p):
        p = p.upper()
        if self.__get_currency_from_name(p):
            return self.__get_rate_with_code(self.__get_currency_from_name(p))
        elif self.__get_currency_from_code(p):
            return self.__get_rate_with_code(self.__get_currency_from_code(p))
        else:
            return self.__get_rate_with_code(p)

    def __get_rate_with_code(self, name):
        if name is None:
            return
        else:
            if name == 'USD':
                return 1.0
            resources = self.resources
            for resource in resources:
                r = resource['resource']
                if r['fields']['name'] == 'USD/' + str(name):
                    return float(r['fields']['price'])

    def map_to_code(self, name):
        name = name.upper()
        if self.maps['name_to_currency'].get(name):
            return self.maps['name_to_currency'].get(name)
        elif self.maps['code_to_currency'].get(name):
            return self.maps['code_to_currency'].get(name)
        else:
            return name

    def trans_currency(self, from_, to, amount, accuracy=3):
        from_rate = self.get_multifunctional(from_)
        to_rate = self.get_multifunctional(to)
        price = amount / from_rate * to_rate
        result = {}
        result['price'] = round(price, accuracy)
        result['from'] = from_
        result['to'] = to
        return result
