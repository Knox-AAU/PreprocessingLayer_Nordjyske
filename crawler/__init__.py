"""
This module can take the following input:
- 1) path
- 2) (Optional) formDate YYYY-MM-DD If not provided, it will start from beginning of data
- 3) (Optional) toDate YYYY-MM-DD If not provided, it will start from beginning of data
- 4) (Optional) --clearcache
https://docs.python.org/3/library/argparse.html

python __init__.py -from 2020-04-10 --clearcache
"""
import argparse
import math
import re
from crawler.crawl import run_crawler

def perfect_square(string):
     value = int(string)
     sqrt = math.sqrt(value)
     if sqrt != int(sqrt):
         msg = "%r is not a perfect square" % string
         raise argparse.ArgumentTypeError(msg)
     return value


def parse_date(date):
    pattern = re.compile("\d\d\d\d-\d\d-\d\d")
    if re.match(pattern, date):
        out_date = {
            'year': int(date[0:4]),
            'month': int(date[5:7]),
            'date': int(date[8:10])
        }
        return out_date
    else:
        msg = f"{date} is not a correctly formatted date"
        raise argparse.ArgumentTypeError(msg)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='The root to crawl.')
    parser.add_argument('-t', '--to', dest="toDate", type=parse_date, default=argparse.SUPPRESS,
                        help='defines the end date from the collected data. It should be formatted as YYYY-MM-DD. (Default: no)')

    parser.add_argument('-f', '--from', dest="fromDate", type=parse_date, default=argparse.SUPPRESS,
                        help='defines the end date from the collected data. It should be formatted as YYYY-MM-DD. (Default: no)')

    parser.add_argument('-cc', '--clearcache', action='store_true',
                        help='clear the folders.json cache. Should only be used if dataset has changed. (Default: no)')

    args = parser.parse_args()

    run_crawler(args)

