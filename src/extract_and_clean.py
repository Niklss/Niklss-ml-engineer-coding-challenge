import asyncio
import gc
import logging
import sys
from itertools import islice
from multiprocessing import Process, cpu_count

import lxml.etree as ET
import pyarrow as pa
import pyarrow.parquet as pq

from src.cleaner import HTMLTags, MTCleaner, MTCleanerPipeline, MarkupTags, Strip, XMLTags, re

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


class CustomCleaner(MTCleaner):
    """
    This class is just an example of writing some custom cleaner.
    """

    @staticmethod
    def __call__(text, *args, **kwargs) -> str:
        text = re.sub(r'\xa0', '', text)
        text = re.sub(r'br ?/', '', text)
        text = re.sub(r'/br', '', text)
        return text


class TMXCleaner:
    """
    This class joins the cleaner and the reader of the file.
    """

    def __init__(self, tmx_file, output_file, processes=4):
        """
        It initializes a cleaning pipeline.
        """
        self.pipeline = MTCleanerPipeline([HTMLTags(), XMLTags(), MarkupTags(), Strip(), CustomCleaner()])
        self.tmx_file = tmx_file
        self.output_file = output_file
        self.processes = processes
        self.tmx_schema = None
        self.writer = None

    @staticmethod
    def _tmx_reader(tmx_file) -> iter:
        """
        :param tmx_file: the path of the tmx file.
        :return: iterable to load iteratively the data from the file.
        """
        with open(tmx_file, "rb") as f:
            tree = ET.iterparse(f, tag=['tu'])
            for event, elem in tree:
                yield tuple(ET.tostring(tuv.find("seg"), encoding="unicode") for tuv in elem.iter("tuv"))
                elem.clear()
                for ancestor in elem.xpath('ancestor-or-self::*'):
                    while ancestor.getprevious() is not None:
                        del ancestor.getparent()[0]
            del tree

    def _write(self, res):
        if not self.tmx_schema or not self.writer:
            self.tmx_schema = pa.schema([pa.field(f'lang-{idx}', pa.string()) for idx, text in enumerate(res[0])])
            self.writer = pq.ParquetWriter(self.output_file, self.tmx_schema)

        data_table = pa.Table.from_pylist(res, self.tmx_schema)
        self.writer.write_table(data_table)

    def _clean_and_write(self, data, idx):
        cleaned_row = [self.pipeline(row) for row in data]
        self._write(cleaned_row)

    @staticmethod
    def chunks(iterable, size=10):
        iterator = iter(iterable)
        return islice(iterator, size)

    async def run(self):
        """
        Creates a generator to iterate through the data during runtime. Using multiprocessing pool creates multiple
        processes with  chunks of data to clean and write the result into parquet file.
        :return:
        """
        file_generator = self._tmx_reader(self.tmx_file)

        logging.info(msg='Started cleaning')
        chunk_size = 10000
        counter = 0
        slice = True
        while slice:
            process_list = []
            for i in range(self.processes):
                slice = list(self.chunks(file_generator, size=chunk_size))
                if not slice:
                    break
                counter += 1
                process = Process(target=self._clean_and_write, args=(slice, counter))
                # process = self._clean_and_write(slice, counter)
                process.start()
                process_list.append(process)

            for process in process_list:
                process.join()
                process.close()

            gc.collect()
            print(f'{sys.getsizeof(self)=} {sys.getsizeof(slice)=} {sys.getsizeof(process_list)=} {sys.getsizeof(file_generator)=}')
            logging.info(msg=f'Processed {counter * chunk_size} rows.')


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    tmx_cleaner = TMXCleaner('../resources/de-en.tmx', '../results/output.parquet', cpu_count() * 2)
    event_loop.run_until_complete(tmx_cleaner.run())
