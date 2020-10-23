import asyncio
import multiprocessing
import os
from datetime import datetime, timezone
from queue import Queue
from random import random
from multiprocessing import Process, Queue, cpu_count

from joblib import Parallel, delayed

from crawler.crawl import Crawler

# https://asyncio.readthedocs.io/en/latest/producer_consumer.html
from crawler.file_types import FileType
from initial_ocr.teseract_module import TesseractModule
from mother.save_to_json import save_to_json
from nitf_parser.parser import NitfParser


def consumer(i, q): #todo move into class
    while True:
        # wait for an item from the producer
        print(f'Waiting on new item...')
        item = q.get()
        if item is None:
            # the producer emits None to indicate that it is done
            break
        print(f'[Thread {i}] consuming item {item.__dict__}...')

        publications = Parallel(n_jobs=multiprocessing.cpu_count(), prefer="threads")(
            delayed(__process_file)(file)
            for file in item.files)

        save_to_json("./json_out", publications)  # todo get from args

        print(f'[Thread {i}] done with item {item.__dict__}...')


def __process_file(file):
    if file.type == FileType.JP2:
        # run OCR
        return TesseractModule().run_tesseract_on_image(file.path)  # todo exchange files
    if file.type == FileType.NITF:
        # run NITF parser
        return NitfParser().parse(file.path)  # todo exchange files
    #todo empty paragraphs and only one article pr. for some reason.


class MotherRunner:
    def __init__(self, path):
        self.q = Queue()
        self.worker_count = 1
        self.workers = []

    def __producer(self, path):
        Crawler().crawl_folders(self.q, path)

        # indicate we are done adding to queue
        self.q.put(None)

    def start(self, path):
        print("starting %d workers" % self.worker_count)
        self.workers = [Process(target=consumer, args=(i, self.q))
                        for i in range(self.worker_count)]
        for w in self.workers:
            w.start()

        self.__producer(path)

        self.stop()

    def stop(self):
        print(f"stopping {self.worker_count} workers")
        self.q.put(None)
        for i in range(self.worker_count):
            self.workers[i].join()
        self.q.close()
