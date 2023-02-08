import asyncio
import logging
import pathlib
from itertools import islice
from multiprocessing import Pool, cpu_count

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

    def __init__(self, tmx_file, output_file, processes=4, chunk_size=10000):
        """
        It initializes a cleaning pipeline.
        """
        self.pipeline = MTCleanerPipeline([HTMLTags(), XMLTags(), MarkupTags(), Strip(), CustomCleaner()])
        self.tmx_file = tmx_file
        self.output_file = pathlib.Path(output_file)
        self.chunk_size = chunk_size
        self.base = self.output_file.with_suffix('').absolute()
        self.base.mkdir(parents=True, exist_ok=True)
        self.processes = processes
        self.tmx_schema = None

    @staticmethod
    def _tmx_reader(tmx_file) -> iter:
        """
        Read the file using lxml etree and clear the tree to free memory.
        :param tmx_file: the path of the tmx file.
        :return: iterable to load iteratively the data from the file.
        """
        with open(tmx_file, "rb") as f:
            tree = ET.iterparse(f, events=('end',), tag=['tu'])
            for event, elem in tree:
                yield tuple(ET.tostring(tuv.find("seg"), encoding="unicode") for tuv in elem.iter("tuv"))
                elem.clear()
            del tree

    def _write(self, res, file_index):
        """
        Formats the rows into dicts to save into parquet dataset folder.
        :param res: Rows of strings.
        :param file_index: Index of the file.
        :return:
        """
        if not self.tmx_schema:
            self.tmx_schema = pa.schema([pa.field(f'lang-{idx}', pa.string()) for idx, text in enumerate(res[0])])
        columns = [dict(zip(self.tmx_schema.names, i)) for i in res]
        data_table = pa.Table.from_pylist(columns, self.tmx_schema)
        pq.write_table(data_table, self.base.absolute() / f"{self.base.name}-{file_index}.parquet")

    def _clean_and_write(self, data, file_index):
        """
        For easier pool starting.
        :param data: Rows of strings.
        :param file_index: Index of the file.
        :return:
        """
        cleaned_rows = [x for row in data if (x := self.pipeline(row)) and all(x)]
        self._write(cleaned_rows, file_index)  # Write dataset under it's id

    @staticmethod
    def chunks(iterable, size=1000):
        """
        Was written for apply_async.
        :param iterable: any generator.
        :param size: the amount of iterations to crop.
        :return:
        """
        iterator = iter(iterable)
        return islice(iterator, size)

    async def run(self):
        """
        Creates a generator to iterate through the data during runtime. Using multiprocessing pool creates multiple
        processes with chunks of data to clean and write the result into parquet dataset file.
        :return:
        """
        file_generator = self._tmx_reader(self.tmx_file)

        logging.info(msg='Started cleaning')

        with Pool(processes=self.processes) as pool:  # Creating pool of workers
            counter = 0
            slice = True
            while slice:  # Check on dataset end
                input_slices = [(list(self.chunks(file_generator, size=self.chunk_size)), counter + i) for i in
                                range(self.processes)]  # Slices of rows with file_id for parquet dataset
                [pool.apply_async(self._clean_and_write, args=slice).get() for slice in input_slices if slice[0]]
                counter += self.processes
                slice = input_slices[-1][0]  # Check if empty
                logging.info(msg=f'Processed {counter * self.chunk_size} rows.')


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    tmx_cleaner = TMXCleaner('../resources/de-en.tmx', '../results/output', cpu_count())
    event_loop.run_until_complete(tmx_cleaner.run())

    ds = pq.ParquetDataset('../results/output', use_legacy_dataset=False)
    ds.read()
