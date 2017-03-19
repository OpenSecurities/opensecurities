#!/usr/bin/env python

# core
import argparse
import json
import urllib.request

from pprint import pprint

HELP_STRINGS = {
    'argument_symbol' : 'Fetch quote for provided stock symbol.'
}

def pull_quote(symbol):
    "Download and parse the company quote"

    url = 'http://dev.markitondemand.com/Api/v2/Quote/json?symbol=%s' % symbol
    req = urllib.request.urlopen(url)
    raw = json.loads(req.read().decode('utf-8'))
    quote = {
        'price' : {
            'low' : None,
            'high' : None,
            'open' : None,
            'last_price' : None,
            'change_ytd' : None
        },
        'market' : {
            'market_cap' : None,
            'volume' : None
        }
    }

    quote['price']['low'] = raw['Low']
    quote['price']['high'] = raw['High']
    quote['price']['open'] = raw['Open']
    quote['price']['last_price'] = raw['LastPrice']
    quote['price']['change_ytd'] = raw['ChangeYTD']
    quote['market']['market_cap'] = raw['MarketCap']
    quote['market']['volume'] = raw['Volume']

    return quote

def run():
    "Main program loop"
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbol', help=HELP_STRINGS['argument_symbol'])

    args = parser.parse_args()
    if args.symbol:
        print(json.dumps(pull_quote(args.symbol)))

if __name__ == '__main__':
    run()
