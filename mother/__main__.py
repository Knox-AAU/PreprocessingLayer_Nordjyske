import argparse
import os
import re
from datetime import datetime, timezone
from mother.consume_folders import MotherRunner
os.environ["OPENCV_IO_ENABLE_JASPER"] = "true"


def parse_date(date):
    pattern = re.compile("\\d\\d\\d\\d-\\d\\d-\\d\\d")
    if re.match(pattern, date):
        return datetime(year=int(date[0:4]), month=int(date[5:7]), day=int(date[8:10]), tzinfo=timezone.utc)
    else:
        msg = f"{date} is not a correctly formatted date"
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "The main module of data-processing of input files from a dataset.")

    parser.add_argument("path", help='The root to crawl.')
    parser.add_argument("output_path", help='The root to crawl.')

    # defines from_date argument
    parser.add_argument('-f', '--from', dest="from_date", type=parse_date,
                        default=datetime(year=1, month=1, day=1, tzinfo=timezone.utc),
                        help='defines the end date from the collected data.'
                             ' It should be formatted as YYYY-MM-DD. (Default: no)')

    # defines toDate argument
    parser.add_argument('-t', '--to', dest="to_date", type=parse_date,
                        default=datetime(year=9999, month=1, day=1, tzinfo=timezone.utc),
                        help='defines the end date from the collected data. '
                             'It should be formatted as YYYY-MM-DD. (Default: no)')

    args = parser.parse_args()

    MotherRunner(args.path, args.from_date, args.to_date, args.output_path).start()
