# coding=utf-8

from alfred_xml import AlfredXmlGenerator
from finance_data_operator import FinanceDataOperator
import os
import sys
import urllib
import argparse

# f_handle = open('display.out', 'w')
# x = sys.stdout.encoding
# sys.stdout = f_handle
# w_handle = open('error.out', 'w')
# sys.stderr = w_handle

FINANCE_URL = 'http://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json'
FINANCE_FILE = 'exchange_rate.json'
MAP_FILE = 'codes_map.json'
CHECK_FREQUENCE = 7
ACCURACY = 3
DEFAULT_CURRENCY = {'main': ['CNY'], 'sub': [
    'CNY', 'JPY', 'USD', 'HKD', 'EUR']}
pwd = os.getcwd()
pic_path = os.path.join(pwd, 'flags')
default_icon = os.path.join(pic_path, 'DEFAULT.png')


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
        urllib.urlretrieve(FINANCE_URL, FINANCE_FILE)
        return FinanceDataOperator(FINANCE_FILE, MAP_FILE)

    if not os.path.isfile(FINANCE_FILE):
        do = download_data()
    else:
        do = FinanceDataOperator(FINANCE_FILE, MAP_FILE)

    days = do.days_til_now()
    if days > CHECK_FREQUENCE:
        do = download_data()
    return do


def get_argv():
    if len(sys.argv) == 1:
        return None
    else:
        argv = [i.upper() for i in sys.argv[1:]]
        return argv


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


def check_set_syntax(argv, do):
    synatax_error = SyntaxError()
    synatax_error.text = 'usage: set default <country_code>'
    if argv[0] == 'SET':
        if 'DEFAULT' in argv:
            if len(argv) == 3:
                if do.get_multifunctional(argv[2]) is None:
                    currency = argv[2]
                    key_error = KeyError()
                    key_error.key = currency
                    key_error.text = "Can't find key: %s" % currency
                    raise key_error
            else:
                raise synatax_error
        else:
            raise synatax_error


def check_syntax(argv, do):
    synatax_error = SyntaxError()
    synatax_error.text = 'usage: <code> <code> <amount> or <country> <country> <amount> or <amount>'
    if 'SET' == argv[0]:
        check_set_syntax(argv, do)
    elif len(argv) == 1:
        try:
            float(argv[0])
        except ValueError:
            raise synatax_error
    elif len(argv) == 2:
        currency = argv[0]
        if do.get_multifunctional(currency) is None:
            key_error = KeyError()
            key_error.key = currency
            key_error.text = "Can't find key: %s" % currency
            raise key_error
    elif len(argv) == 3:
        for i in range(2):
            currency = argv[i]
            if do.get_multifunctional(currency) is None:
                key_error = KeyError()
                key_error.key = currency
                key_error.text = "Can't find key: %s" % currency
                raise key_error
        try:
            float(argv[2])
        except ValueError:
            raise synatax_error
    else:
        raise synatax_error


def type_of(argv):
    if argv is None:
        return
    elif len(argv) == 3 and argv[0] == 'SET' and argv[1] == 'DEFAULT':
        return 'set_default'
    elif len(argv) == 1:
        return 'default'
    elif len(argv) == 3:
        return 'normal'
    elif len(argv) == 2:
        return 'single'


def format_result(result, do):
    for i in result:
        for key in i:
            if do.get_currency_from_anything(i[key]) != 'EUR':
                i[key] = do.get_currency_from_anything(i[key])


def main():
    do = get_newest_data()
    argv = get_argv()
    check_syntax(argv, do)
    result = []
    if type_of(argv) is None:
        return
    elif type_of(argv) == 'default':
        amount = float(argv[0])
        for i in combination_of_dict(DEFAULT_CURRENCY):
            t = {}
            t = do.trans_currency(i[0], i[1], amount, ACCURACY)
            result.append(t)
    elif type_of(argv) == 'normal':
        from_ = do.map_to_code(argv[0])
        to = do.map_to_code(argv[1])
        amount = float(argv[2])
        t = do.trans_currency(from_, to, amount, ACCURACY)
        result.append(t)
        t = do.trans_currency(to, from_, amount, ACCURACY)
        result.append(t)
    elif type_of(argv) == 'single':
        amount = float(argv[1])
        CURRENCY_DICT = DEFAULT_CURRENCY.copy()
        CURRENCY_DICT['main'] = argv[0:1]
        for i in combination_of_dict(CURRENCY_DICT):
            t = {}
            t = do.trans_currency(i[0], i[1], amount, ACCURACY)
            result.append(t)
    elif type_of(argv) == 'set_default':
        DEFAULT_CURRENCY['main'] = argv[2]

    format_result(result, do)
    print_result(result)

if __name__ == '__main__':
    try:
        main()
    except SyntaxError as e:
        AlfredXmlGenerator.print_error('Incorrect Syntax', e.text)
    except KeyError as e:
        AlfredXmlGenerator.print_error('Invalid Key', e.text)
    except UnicodeDecodeError:
        AlfredXmlGenerator.print_error(
            "Sorry...", "But we don't support Chinese... yet")
    # except:
    #     AlfredXmlGenerator.print_error('Unknown', 'a')
