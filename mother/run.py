import asyncio
from queue import Queue
from random import random

from crawler.crawl import Crawler
#https://asyncio.readthedocs.io/en/latest/producer_consumer.html

class MotherRunner:
    def __init__(self, path):
        self.loop = asyncio.get_event_loop()
        self.q = asyncio.Queue(loop=self.loop)
        self.producer = MotherRunner.__produce(self.q, path)
        self.consumer = MotherRunner.__consume(self.q)

    @staticmethod
    async def __produce(q, path):
        print("Starting producer...")
        await Crawler().run_crawler(path)

        # put the none item in queue, to indicate end of queue.
        await q.put(None)

    @staticmethod
    async def __consume(q):
        while True:
            # wait for an item from the producer
            item = await q.get()
            if item is None:
                # the producer emits None to indicate that it is done
                break

            # process the item
            print('consuming item {}...'.format(item))
            # simulate i/o operation using sleep
            await asyncio.sleep(random())

    def run(self, args):
        print(args.__dict__)
        self.loop.run_until_complete(asyncio.gather(self.producer,self.consumer))
        self.loop.close()
