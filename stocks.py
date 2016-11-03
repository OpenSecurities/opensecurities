#!/usr/bin/env python
""" Pulls down a list of stocks and outputs them as JSON. """

# core
import argparse
import json
import re
import urllib.request

# 3rd party
import feedparser

import pprint

HELP_STRINGS = {
    'argument_symbol' : 'Only fetch results for provided stock symbol',
    'argument_list' : 'Fetch a list of publicly traded stock symbols.'
}

def process_rss(string, child):
    "Process RSS passed as a string"

    stock = {
        'name' : None,
        'cik' : None,
        'address' : {
            'street1' : None,
            'street2' : None,
            'state' : None,
            'city' : None,
            'zip' : None
        },
        'phone' : None
    }

    info = feedparser.parse(string)['feed']
    stock['cik'] = info['cik']
    stock['name'] = info['conformed-name']
    stock['phone'] = info['phone']
    stock['address']['street1'] = info['street1']
    stock['address']['state'] = info['state']
    stock['address']['city'] = info['city']
    stock['address']['zip'] = info['zip']

    return stock

def symbol_list():
    "Fetch and return a list of stock symbols."

    # Fetch data from NASDAQ
    companies = []
    for exchange in ['nasdaq', 'nyse']:
        url = 'http://www.nasdaq.com/screening/companies-by-name.aspx?' \
                + 'letter=0&%s=nasdaq&render=download' % exchange

        req = urllib.request.urlopen(url)
        for line in req.read().decode('utf-8').split('\r\n'):
            line = re.sub('"', '', line)
            components = line.split(',')
            if len(components) > 1:
                symbol = components[0]
                name = components[1]
                if symbol != 'Symbol':
                    companies.append({
                        'symbol' : symbol,
                        'name' : name
                    })

    return companies

def symbol_search(symbol):
    "Search for company data via stock symbol"
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?'\
            + 'action=getcompany&CIK=%s' % symbol\
            + '&type=&dateb=&owner=exclude&start=0&count=40&output=atom'

    req = urllib.request.urlopen(url)
    return process_rss(req.read().decode('utf-8'), 'company-info')

def run():
    "Main program loop"
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbol', help=HELP_STRINGS['argument_symbol'])
    parser.add_argument('-l', '--list', \
            help=HELP_STRINGS['argument_list'],action="store_true", \
            default=False)
    args = parser.parse_args()

    if args.symbol:
        print(json.dumps(symbol_search(args.symbol)))
    elif args.list:
        print(json.dumps(symbol_list()))

if __name__=='__main__':
    run()
