#!/usr/bin/env python

import argparse
import configparser
from datetime import datetime
import json
from os import path, listdir, rename
import re
import tempfile
import urllib.request
import zipfile

HELP_STRINGS = {
    'symbol' : 'Only fetch results for provided stock symbol',
    'historic' : 'Fetch all the historic prices',
    'post' : 'POST the acquired data to this endpoint.',
    'from' : 'Retrive prices starting with, but not including, the provided date.',
    'today' : "Return only todays prices."
}

QUANDL_KEY = ''

def load_config():
    "Loads a config from the home directory"
    home = path.expanduser('~')
    config_path = path.join(home, '.opensecurities')
    config = configparser.ConfigParser()
    config.readfp(open(config_path))

    global QUANDL_KEY

    QUANDL_KEY = config.get('quandl', 'api_key')

def transform(price):
    "Transform from the Quandl format to the OS format."
    n = {
        'symbol' : price[0],
        'date' : price[1],
        'open' : price[2],
        'high' : price[3],
        'low' : price[4],
        'close' : price[5],
        'volume' : int(price[6]),
        'ex_dividend' : price[7],
        'split_ratio' : price[8],
        'adj_open' : price[9],
        'adj_high' : price[10],
        'adj_low' : price[11],
        'adj_close' : price[12],
        'adj_volume' : int(price[13])
    }

    return n

def get_historic(symbol):
    "Download the historic prices for the provided stock."
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?'
    url = '%sticker=%s' % (url, symbol)
    url = '%s&qopts.export=true' % url
    url = '%s&api_key=%s' % (url, QUANDL_KEY)

    prices = []

    req = urllib.request.urlopen(url)
    resp = json.loads(req.read().decode('utf-8'))

    download_link = resp['datatable_bulk_download']['file']['link']

    # Download the zip and extract the CSV
    with tempfile.TemporaryDirectory() as work_dir:
        req = urllib.request.urlopen(download_link)

        with open(path.join(work_dir, 'prices.zip'), 'wb') as z_file:
            z_file.write(req.read())

        with zipfile.ZipFile(path.join(work_dir, 'prices.zip')) as zip:
            for file in zip.namelist():
                if re.search('\.csv$', file):
                    zip.extract(file, work_dir)
                    rename(
                        path.join(work_dir, file),
                        path.join(work_dir, 'prices.csv')
                    )


        if 'prices.csv' not in listdir(work_dir):
            return None

        columns = []

        for i, line in enumerate(open(path.join(work_dir, 'prices.csv'))):

            if i == 0:
                for col in line.split(','):
                    col = col.replace('\n', '')
                    if col == "ticker":
                        col = 'symbol'
                    elif col == 'ex-dividend':
                        col = 'ex_dividend'

                    columns.append(col)
            else:
                if not columns:
                    print('Error reading header')
                    return None
                
                obj = {}
                for y, col in enumerate(line.split(',')):
                    col_name = columns[y]
                    col = col.replace('\n', '')

                    # Convert the volume fields
                    if re.search('volume', col_name):
                        col = int(float(col))
                    else:
                        # Try to convert string to float if possible
                        try:
                            col = float(col)
                        except ValueError:
                            pass

                    obj.update({
                        columns[y] : col
                    })

                prices.append(obj)

    return prices

def get_today(symbol):
    "Download the most recently available EOD prices."

    datestamp = datetime.now().strftime('%Y-%m-%d')
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?'
    url = '%sticker=%s' % (url, symbol)
    url = '%s&date=%s' % (url, datestamp)
    url = '%s&api_key=%s' % (url, QUANDL_KEY)

    req = urllib.request.urlopen(url)
    resp = json.loads(req.read().decode('utf-8'))

    if len(resp['datatable']['data']) == 0:
        print('No results available')

        return None

    return transform(resp['datatable']['data'][0])

def get_from_date(symbol, from_date):
    "Download all price data starting with, but not including, the from_date"

    datestamp = datetime.now().strftime('%Y-%m-%d')
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?'
    url = '%sticker=%s' % (url, symbol)
    url = '%s&date.gt=%s' % (url, from_date)
    url = '%s&api_key=%s' % (url, QUANDL_KEY)

    req = urllib.request.urlopen(url)
    resp = json.loads(req.read().decode('utf-8'))

    results = resp['datatable']['data']

    if len(results) == 0:
        print('No results available')

        return None
    elif len(results) == 1:
        # Single result
        return transform(results[0])
    else:
        prices = []
        for r in results:
            prices.append(transform(r))

        return prices

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
        print(e.read().decode('utf-8'))
        return None

def run():
    "Main program loop"
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbol', help=HELP_STRINGS['symbol'])
    parser.add_argument('-i', '--historic', help=HELP_STRINGS['historic'], \
            action="store_true", default=False)
    parser.add_argument('-t', '--today', help=HELP_STRINGS['today'], \
            action="store_true", default=True)
    parser.add_argument('-p', '--post', help=HELP_STRINGS['post'])
    parser.add_argument('-f', '--from-date', help=HELP_STRINGS['from'])

    args = parser.parse_args()
    result = None

    load_config()

    if args.symbol:
        if args.historic:
            result = get_historic(args.symbol)
        elif args.from_date:
            result = get_from_date(args.symbol, args.from_date)
        elif args.today:
            result = get_today(args.symbol)

    if result != None:

        if args.post:
            send = post_results(args.post, json.dumps(result))
            if send != None:
                print(send)
        else:
            print(json.dumps(result))

if __name__ == '__main__':
    run()
