# -*- coding: utf-8 -*-

from alfred_xml import AlfredXmlGenerator
from finance_data_operator import FinanceDataOperator
import os
import subprocess
import sys
import re

FINANCE_URL = 'http://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json'
FINANCE_FILE = 'exchange_rate.json'
MAP_FILE = 'chinese_code_map.json'
CHECK_FREQUENCE = 7
DEFAULT_CURRENCY = ['CNY', 'JPY', 'USD']
ACCURACY = 3


def combination_of_list(l, list_):
    if l == 0:
        return [[]]
    elif list_ == []:
        return []
    result = []
    for i, t in enumerate(list_):
        new_list = list_[:i] + list_[i+1:]
        result += ([[t] + j for j in combination_of_list(l-1, new_list)])
    return result


def get_newest_data():
    def download_data():
        subprocess.call(['wget', '-c', FINANCE_URL, '-O', FINANCE_FILE])
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
    # AlfredXmlGenerator.print_error('Unknown Error', str(sys.argv[1]))
    if len(sys.argv) == 1:
        return None
    else:
        raw_argv = sys.argv[1]
        if raw_argv[-1] == ' ':
            raw_argv = raw_argv[:-1]
        argv = re.split(r'\s+', raw_argv)
        return argv


def print_result(result):
    alfred_xml = AlfredXmlGenerator()

    for i in result:
        display_text = i['from'] + '->' + i['to']
        alfred_xml.add_item(display_text, str(i['price']))
    alfred_xml.print_xml()


def check_syntax(argv, do):
    synatax_error = SyntaxError()
    synatax_error.text = 'usage: <from_code> <to_code> <amount> or <country> <country> <amount> or <amount>'
    if len(argv) == 1:
        try:
            float(argv[0])
        except ValueError:
            raise synatax_error
    elif len(argv) == 3:
        for i in range(2):
            currency = argv[i]
            if do.get_rate(currency) is None:
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


def main():
    do = get_newest_data()
    argv = get_argv()
    check_syntax(argv, do)
    result = []
    if argv is None:
        return
    elif len(argv) == 1:
        amount = float(argv[0])
        for i in combination_of_list(2, DEFAULT_CURRENCY):
            t = {}
            t = do.trans_currency(i[0], i[1], amount, ACCURACY)
            result.append(t)
    elif len(argv) == 3:
        from_ = argv[0]
        to = argv[1]
        amount = float(argv[2])
        t = do.trans_currency(from_, to, amount, ACCURACY)
        result.append(t)

    print_result(result)

if __name__ == '__main__':
    try:
        main()
    except SyntaxError as e:
        AlfredXmlGenerator.print_error('Incorrect Syntax', e.text)
    except KeyError as e:
        AlfredXmlGenerator.print_error('Invalid Key', e.text)
    except:
        AlfredXmlGenerator.print_xml('Unknown', 'a')
