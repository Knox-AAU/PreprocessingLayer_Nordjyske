import argparse
import os
import re
from datetime import datetime, timezone
from consume_folders import MotherRunner

os.environ["OPENCV_IO_ENABLE_JASPER"] = "true"


def parse_date(date):
    pattern = re.compile("\\d\\d\\d\\d-\\d\\d-\\d\\d")
    if re.match(pattern, date):
        return datetime(
            year=int(date[0:4]),
            month=int(date[5:7]),
            day=int(date[8:10]),
            tzinfo=timezone.utc,
        )
    else:
        msg = f"{date} is not a correctly formatted date"
        raise argparse.ArgumentTypeError(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "The main module of data-processing of input files from a dataset."
    )

    parser.add_argument("path", help="The root to crawl.")
    parser.add_argument("output_path", help="The path to output folder.")

    # defines from_date argument
    parser.add_argument(
        "-f",
        "--from",
        dest="from_date",
        type=parse_date,
        default=None,
        help="defines the end date from the collected data."
        " It should be formatted as YYYY-MM-DD. (Default: no)",
    )

    # defines toDate argument
    parser.add_argument(
        "-t",
        "--to",
        dest="to_date",
        type=parse_date,
        default=None,
        help="defines the end date from the collected data. "
        "It should be formatted as YYYY-MM-DD. (Default: no)",
    )

    # defines the optiion to POST the json parsed to the next layer
    parser.add_argument(
        "-p",
        "--post",
        dest="post",
        action="store_true",
        default=False,
        help="defines the option to POST the json parsed to the next layer. ",
    )

        # defines the optiion to POST the json parsed to the next layer
    parser.add_argument(
        "-db",
        "--database",
        dest="db",
        action="store_true",
        default=False,
        help="defines the option to POST the json parsed to the MongoJsonAPI. ",
    )

    args = parser.parse_args()

    MotherRunner(
        args.path, args.from_date, args.to_date, args.output_path, args.post, args.db
    ).start()
