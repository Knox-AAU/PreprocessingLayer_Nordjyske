import argparse
import re
from crawler.crawl import Crawler


def parse_date(date):
    pattern = re.compile("\\d\\d\\d\\d-\\d\\d-\\d\\d")
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
    # defines input and output path
    parser.add_argument('path', help='The root to crawl.')
    parser.add_argument('output_folder', help='The folder in which to save json outputs.')

    # defines toDate argument
    parser.add_argument('-t', '--to', dest="to_date", type=parse_date, default=argparse.SUPPRESS,
                        help='defines the end date from the collected data. It should be formatted as YYYY-MM-DD. (Default: no)')

    # defines from_date argument
    parser.add_argument('-f', '--from', dest="from_date", type=parse_date, default=argparse.SUPPRESS,
                        help='defines the end date from the collected data. It should be formatted as YYYY-MM-DD. (Default: no)')

    # defines clear cache argument
    parser.add_argument('-cc', '--clearcache', action='store_true',
                        help='clear the folders.json cache. Should only be used if dataset has changed. (Default: no)')

    parser.add_argument('-o', '--output', dest="output_folder", default="./output/",
                        help='Optional output path, which a json file will be saved to.')
    args = parser.parse_args()
    crawler = Crawler()
    crawler.run_crawler(args)
