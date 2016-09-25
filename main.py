# coding=utf-8

from alfred_xml import AlfredXmlGenerator
from finance_data_operator import FinanceDataOperator
import os
import urllib2
import argparse
import sys

# f_handle = open('display.out', 'w')
# x = sys.stdout.encoding
# sys.stdout = f_handle
# w_handle = open('error.out', 'w')
# sys.stderr = w_handle

# FINANCE_URL = 'http://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json'
FINANCE_URL = 'http://api.fixer.io/latest?base=USD'
FINANCE_FILE = 'exchange_rate.json'
MAP_FILE = 'codes_map.json'
CHECK_FREQUENCE = 7
ACCURACY = 3
DEFAULT_CURRENCY = {'main': ['CNY'], 'sub': [
    'CNY', 'JPY', 'USD', 'HKD', 'EUR']}
pwd = os.getcwd()
pic_path = os.path.join(pwd, 'flags')
default_icon = os.path.join(pic_path, 'DEFAULT.png')


class ThrowingArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        raise SyntaxError(message)


def combination_of_dict(dic):
    result = []
    for m in dic['main']:
        for s in dic['sub']:
            if s != m:
                result.append([m, s])
                result.append([s, m])
    return result


def abs_path(path):
    return os.path.join(pwd, path)


def get_newest_data():
    def download_data():
        f = urllib2.urlopen(FINANCE_URL)
        with open(FINANCE_FILE, "wb") as code:
            code.write(f.read())
        return FinanceDataOperator(FINANCE_FILE, MAP_FILE)

    if not os.path.isfile(FINANCE_FILE):
        do = download_data()
    else:
        do = FinanceDataOperator(FINANCE_FILE, MAP_FILE)

    days = do.days_til_now()
    if days > CHECK_FREQUENCE:
        do = download_data()
    return do


def print_result(result):
    alfred_xml = AlfredXmlGenerator()

    for i in result:
        display_text = i['from'] + ' -> ' + i['to']
        icon_path = os.path.join(pic_path, i['from'] + '.png')
        if os.path.isfile(icon_path):
            alfred_xml.add_item(display_text, str(i['price']), icon=icon_path)
        else:
            alfred_xml.add_item(display_text, str(
                i['price']), icon=default_icon)
    alfred_xml.print_xml()


def get_argv():
    parser = ThrowingArgumentParser()
    parser.add_argument('currency_list', nargs='*')
    parser.add_argument('amount', type=float)
    parser.add_argument('--set', nargs='+')
    argv = parser.parse_args()
    argv.currency_list = [i.upper() for i in argv.currency_list]
    return argv


def check_syntax(argv, do):
    for currency in argv.currency_list:
        if do.get_multifunctional(currency) is None:
            key_error = KeyError()
            key_error.key = currency
            key_error.msg = "Can't find key: %s" % currency
            raise key_error


def type_of(argv):
    if argv is None:
        return
    elif argv.set is not None:
        return 'set_default'
    elif len(argv.currency_list) == 0:
        return 'default'
    elif len(argv.currency_list) == 1:
        return 'single'
    elif len(argv.currency_list) == 2:
        return 'normal'


def format_result(result, do):
    for i in result:
        for key in i:
            if do.get_currency_from_anything(i[key]) != 'EUR':
                i[key] = do.get_currency_from_anything(i[key])


def handle_argv(argv, do):
    result = []
    if type_of(argv) is None:
        return
    elif type_of(argv) == 'default':
        amount = argv.amount
        for i in combination_of_dict(DEFAULT_CURRENCY):
            t = {}
            t = do.trans_currency(i[0], i[1], amount, ACCURACY)
            result.append(t)
    elif type_of(argv) == 'normal':
        from_ = do.map_to_code(argv.currency_list[0])
        to = do.map_to_code(argv.currency_list[1])
        amount = argv.amount
        t = do.trans_currency(from_, to, amount, ACCURACY)
        result.append(t)
        t = do.trans_currency(to, from_, amount, ACCURACY)
        result.append(t)
    elif type_of(argv) == 'single':
        amount = argv.amount
        CURRENCY_DICT = DEFAULT_CURRENCY.copy()
        CURRENCY_DICT['main'] = [argv.currency_list[0]]
        for i in combination_of_dict(CURRENCY_DICT):
            t = do.trans_currency(i[0], i[1], amount, ACCURACY)
            result.append(t)
    elif type_of(argv) == 'set_default':
        pass
    return result


def main():
    do = get_newest_data()
    argv = get_argv()
    check_syntax(argv, do)
    result = handle_argv(argv, do)
    format_result(result, do)
    print_result(result)

if __name__ == '__main__':
    try:
        main()
    except SyntaxError as e:
        AlfredXmlGenerator.print_error({'Incorrect Syntax': e.msg if hasattr(e, 'msg') else ''})
        raise e
    except KeyError as e:
        AlfredXmlGenerator.print_error({'Incorrect Syntax': e.msg if hasattr(e, 'msg') else ''})
        raise e
    # except UnicodeDecodeError:
    #     AlfredXmlGenerator.print_error({"Sorry...": "But we don't support Chinese... yet"})
    # except:
    #     AlfredXmlGenerator.print_error('Unknown', 'a')
