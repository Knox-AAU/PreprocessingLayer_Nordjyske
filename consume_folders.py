import multiprocessing
from multiprocessing import Process, Queue
from joblib import Parallel, delayed
from crawler.crawl import Crawler
from crawler.file_types import FileType
from ocr.ocr_runner import OCRRunner
from save_to_json import save_to_json
from nitf_parser.parser import NitfParser
from knox_source_data_io.io_handler import IOHandler
import traceback
import requests
import json 

class MotherRunner:
    def __init__(self, root, from_date, to_date, output_dest):
        self.q = Queue()
        self.consumer = Process(target=self._consumer)
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

            #print(f'[Consumer Thread] consuming item {item.__dict__}...')

            num_jobs = int((multiprocessing.cpu_count()/2))
            publications = Parallel(n_jobs=num_jobs, prefer="threads")(
                delayed(self.__process_file)(file)
                for file in item.files)
            json_str = save_to_json(self.output_dest, publications)
            try:
                json_obj = json.loads(json_str)
                IOHandler.validate_json(json_obj, "publication.schema.json")
                x = requests.post("http://130.225.57.27/uploadjsonapi/uploadJsonDoc", json = json_obj)
                if (x.status_code != 200):
                    raise Exception("POST error") # better defined
            except Exception as e:
                traceback.print_exc(e)
            print(f'[Consumer Thread] done with item {item.__dict__}...')
            
    def __producer(self):
        Crawler().crawl_folders(self.q, self.root, self.from_date, self.to_date)

        # indicate we are done adding to queue
        self.q.put(None)

    def start(self):
        print("Starting consumer")
        self.consumer.start()

        self.__producer()

        self.consumer.join()