#!/usr/bin/env python
""" Pulls down a list of stocks and outputs them as JSON. """

# core
import argparse
import json
import urllib.request

# 3rd party
import feedparser

import pprint

HELP_STRINGS = {
    'argument_symbol' : 'Only fetch results for provided stock symbol'
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
    args = parser.parse_args()

    if hasattr(args, 'symbol'):
        print(json.dumps(symbol_search(args.symbol)))

if __name__=='__main__':
    run()
