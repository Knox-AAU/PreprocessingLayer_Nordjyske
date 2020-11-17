import multiprocessing
from queue import Queue
from multiprocessing import Process, Queue
from joblib import Parallel, delayed
from crawler.crawl import Crawler

# https://asyncio.readthedocs.io/en/latest/producer_consumer.html
from crawler.file_types import FileType
from ocr.tesseract import TesseractModule
from save_to_json import save_to_json
from nitf_parser.parser import NitfParser


class MotherRunner:
    def __init__(self, root, from_date, to_date, output_dest):
        self.q = Queue()
        self.worker_count = 1
        self.workers = []
        self.root = root
        self.from_date = from_date
        self.to_date = to_date
        self.output_dest = output_dest

    @staticmethod
    def __process_file(file):
        if file.type == FileType.JP2:
            # run OCR
            return TesseractModule.from_file(file).to_publication()
        if file.type == FileType.NITF:
            # run NITF parser
            return NitfParser().parse_file(file)

    def __consumer(self):
        while True:
            # wait for an item from the producer
            print(f'Waiting on new item...')
            item = self.q.get()
            if item is None:
                # the producer emits None to indicate that it is done
                break

            print(f'[Consumer Thread] consuming item {item.__dict__}...')

            num_jobs = (multiprocessing.cpu_count()/2)
            publications = Parallel(n_jobs=num_jobs, prefer="threads")(
                delayed(self.__process_file)(file)
                for file in item.files)

            save_to_json(self.output_dest, publications)

            print(f'[Consumer Thread] done with item {item.__dict__}...')

    def __producer(self):
        Crawler().crawl_folders(self.q, self.root, self.from_date, self.to_date)

        # indicate we are done adding to queue
        self.q.put(None)

    def start(self):
        print("starting %d workers" % self.worker_count)
        self.workers = [
            Process(target=self.__consumer)
            for i in range(self.worker_count)]
        for w in self.workers:
            w.start()

        self.__producer()

        self.stop()

    def stop(self):
        print(f"stopping {self.worker_count} workers")
        self.q.put(None)
        for i in range(self.worker_count):
            self.workers[i].join()
        self.q.close()
