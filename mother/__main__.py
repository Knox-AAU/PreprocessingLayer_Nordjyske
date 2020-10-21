import argparse
import re
from crawler.crawl import Crawler
from mother.run import MotherRunner


def parse_date(date):
    pattern = re.compile("\\d\\d\\d\\d-\\d\\d-\\d\\d")
    if re.match(pattern, date):
        out_date = {
            'year': int(date[0:4]),
            'month': int(date[5:7]),
            'day': int(date[8:10])
        }
        return out_date
    else:
        msg = f"{date} is not a correctly formatted date"
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "The main module of data-processing of input files from a dataset.")

    parser.add_argument("path", help='The root to crawl.')
    parser.add_argument("output_path", help='The root to crawl.')

    # defines toDate argument
    parser.add_argument('-t', '--to', dest="to_date", type=parse_date, default=argparse.SUPPRESS,
                        help='defines the end date from the collected data. It should be formatted as YYYY-MM-DD. (Default: no)')

    # defines from_date argument
    parser.add_argument('-f', '--from', dest="from_date", type=parse_date,
                        default=argparse.SUPPRESS,
                        help='defines the end date from the collected data. It should be formatted as YYYY-MM-DD. (Default: no)')

    # defines clear cache argument
    parser.add_argument('-cc', '--clearcache', action='store_true',
                        help='clear the folders.json cache. Should only be used if dataset has changed. (Default: no)')
    args = parser.parse_args()

    MotherRunner().run(args)
