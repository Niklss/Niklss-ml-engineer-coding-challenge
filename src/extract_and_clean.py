from multiprocessing import Pool, cpu_count

import lxml.etree as ET
import pyarrow as pa
import pyarrow.parquet as pq

from src.cleaner import HTMLTags, MTCleaner, MTCleanerPipeline, MarkupTags, Strip, XMLTags, re


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

    @staticmethod
    def _tmx_reader(tmx_file) -> iter:
        """
        :param tmx_file: the path of the tmx file.
        :return: iterable to load iteratively the data from the file.
        """
        with open(tmx_file, "rb") as f:
            tree = ET.parse(f)
            root = tree.getroot()

            for body in root.iter("body"):
                for tu in body.iter("tu"):
                    yield tuple(ET.tostring(tuv.find("seg"), encoding="unicode") for tuv in tu.iter("tuv"))

    def run(self):
        """
        Creates a generator to iterate through the data during runtime. Using multiprocessing pool creates multiple
        processes with  chunks of data to clean and write the result into parquet file.
        :return:
        """
        file_generator = self._tmx_reader(self.tmx_file)
        first_row = self.pipeline(file_generator.__next__())

        schema = pa.schema([pa.field(f'lang-{idx}', pa.string()) for idx, text in enumerate(first_row)])
        row = dict(zip(schema.names, first_row))
        data_table = pa.Table.from_pylist([row], schema)

        writer = pq.ParquetWriter(self.output_file, data_table.schema)
        writer.write_table(data_table)

        with Pool(processes=self.processes) as pool:
            for cleaned_segment in pool.imap_unordered(self.pipeline, file_generator, chunksize=1000):
                row = dict(zip(schema.names, cleaned_segment))
                data_table = pa.Table.from_pylist([row], schema)
                writer.write_table(data_table)


if __name__ == "__main__":
    tmx_cleaner = TMXCleaner('../resources/tmx-file.tmx', 'output', cpu_count())
    tmx_cleaner.run()
