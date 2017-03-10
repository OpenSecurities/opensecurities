#!/usr/bin/env python
""" Pulls down a list of stocks and outputs them as JSON. """

# core
import argparse
import json
import re
import urllib.request

# 3rd party
import feedparser

HELP_STRINGS = {
    'argument_symbol' : 'Only fetch results for provided stock symbol',
    'argument_list' : 'Fetch a list of publicly traded stock symbols.',
    'argument_post' : 'POST the acquired data to this endpoint.',
    'argument_collapse' : 'Collapse the returned info into a single level.'
}

def process_rss(string, child, symbol):
    "Process RSS passed as a string"

    stock = {
        'symbol' : None,
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
    stock['symbol'] = symbol
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

def format_collapse(data):
    "Formats the data onto a single level. Handy for use with *nix pipes"

    new_data = {}
    new_data['cik'] = data['cik']
    new_data['symbol'] = data['symbol']
    new_data['name'] = data['name']
    new_data['street1'] = data['address']['street1']
    new_data['street2'] = data['address']['street2']
    new_data['city'] = data['address']['city']
    new_data['state'] = data['address']['state']
    new_data['zip'] = data['address']['zip']

    return new_data

def symbol_search(symbol):
    "Search for company data via stock symbol"
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?'\
            + 'action=getcompany&CIK=%s' % symbol\
            + '&type=&dateb=&owner=exclude&start=0&count=40&output=atom'

    req = urllib.request.urlopen(url)
    return process_rss(req.read().decode('utf-8'), 'company-info', symbol)

def post_results(endpoint, results):
    "HTTP POSTs the results of the script run to the provided endpoint."

    req = urllib.request.Request(
            endpoint,
            data=results.encode('utf8'),
            headers={'content-type': 'application/json'}
    )

    try: 
        response = urllib.request.urlopen(req)
        return response.info()
    except Exception as e:
        print(e)
        return None

def run():
    "Main program loop"
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbol', help=HELP_STRINGS['argument_symbol'])
    parser.add_argument('-l', '--list', \
            help=HELP_STRINGS['argument_list'],action="store_true", \
            default=False)
    parser.add_argument('-c', '--collapse', \
            help=HELP_STRINGS['argument_collapse'],action="store_true", \
            default=False)
    parser.add_argument('-p', '--post', help=HELP_STRINGS['argument_post'])

    args = parser.parse_args()

    if args.symbol:
        rtn = symbol_search(args.symbol)
        rendered_output = ''

        if args.collapse:
            rendered_output = json.dumps(format_collapse(rtn))
        else:
            rendered_output = json.dumps(rtn)

        if args.post:
            send = post_results(args.post, rendered_output)
            if send != None:
                print(send)
        else:
            print(rendered_output)

    elif args.list:
        print(json.dumps(symbol_list()))

if __name__=='__main__':
    run()
