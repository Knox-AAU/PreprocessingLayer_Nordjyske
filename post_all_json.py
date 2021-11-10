import os
from knox_source_data_io.io_handler import IOHandler
import re
import json


def post_all_json(json_path):
    for dirpath, subdirs, files in os.walk(json_path):
        for x in files:
            if x.endswith(".json"):
                json_path = os.path.join(dirpath, x)
                print(json_path)
                with (open(json_path)) as f:
                    data = json.load(f)
                    print(data)
                    IOHandler.post_json(data)


if __name__ == "__main__":
    post_all_json("/home/aau/Desktop/output")
