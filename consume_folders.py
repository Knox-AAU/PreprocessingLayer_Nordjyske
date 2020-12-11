import multiprocessing
from multiprocessing import Process, Queue
from joblib import Parallel, delayed
from crawler.crawl import Crawler
from crawler.file_types import FileType
from ocr.ocr_runner import OCRRunner
from save_to_json import save_to_json
from nitf_parser.parser import NitfParser


class MotherRunner:
    def __init__(self, root, from_date, to_date, output_dest):
        self.q = Queue()
        self.worker = Process(target=self._consumer)
        self.root = root
        self.from_date = from_date
        self.to_date = to_date
        self.output_dest = output_dest

    @staticmethod
    def __process_file(file):
        if file.type == FileType.JP2:
            # run OCR
            return OCRRunner().run_ocr(file)
        if file.type == FileType.NITF:
            # run NITF parser
            return NitfParser().parse_file(file)

    def _consumer(self):
        while True:
            # wait for an item from the producer
            print(f'Waiting on new item...')
            item = self.q.get()
            if item is None:
                # the producer emits None to indicate that it is done
                print("Finished all items, exiting.")
                return

            print(f'[Consumer Thread] consuming item {item.__dict__}...')

            num_jobs = int((multiprocessing.cpu_count()/2))
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
        print("Starting consumer")
        self.worker.start()

        self.__producer()

        self.stop()

    def stop(self):
        print("Stopping consumer worker")
        self.q.put(None)
        self.worker.join()