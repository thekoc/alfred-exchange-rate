import json
import datetime


class FinanceDataOperator(object):
    def __init__(self, resource_name, map_name):
        with open(resource_name, 'r') as f:
            self.resources = json.load(f)
        with open(map_name, 'r') as f:
            self.maps = json.load(f)

    def __get_currency_from_name(self, name):
        return self.maps['name_to_currency'].get(name)

    def __get_currency_from_code(self, code):
        return self.maps['code_to_currency'].get(code)

    def get_currency_from_anything(self, anything):
        if self.__get_currency_from_code(anything):
            return self.__get_currency_from_code(anything)
        elif self.__get_currency_from_name(anything):
            return self.__get_currency_from_name(anything)
        else:
            return anything

    def get_time(self):
        raw_time = self.resources['date']
        date = datetime.datetime.strptime(raw_time, '%Y-%m-%d')
        return date

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
            else:
                return self.resources['rates'][name]

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
