import argparse
import logging
import os
import pathlib
from pathlib import Path

import pyarrow.parquet as pq
from numpy import dot
from numpy.linalg import norm

from src.laser.source.embed import SentenceEncoder

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


class SimilarEmbedding:
    def __init__(self, threshold):
        model_dir = Path(os.getenv('LASER')) / "models"
        encoder_path = model_dir / "bilstm.93langs.2018-12-26.pt"
        self.threshold = threshold
        print(f' - Encoder: loading {encoder_path}')
        self.encoder = SentenceEncoder(encoder_path, max_sentences=None, max_tokens=12000, sort_kind='mergesort',
                                       cpu=True)

    def __call__(self, texts: list | tuple, *args, **kwargs) -> bool:
        res = self.encoder.encode_sentences(texts).astype(float)
        a = res[0]
        b = res[1]
        similarity = dot(a, b) / (norm(a) * norm(b))

        return similarity >= self.threshold


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean pairwise translated text from parquet file/dataset')
    parser.add_argument('--dataset-file', type=str, required=True, help='Path to parquet file/dataset')
    parser.add_argument('--output', type=str, required=True, help='Path to output file')
    parser.add_argument('--similarity-threshold', type=float, required=False, help='The limit of the rows to '
                                                                                   'process', default=1)
    parser.add_argument('--limit', type=int, required=False, help='The limit of the rows to process')
    args = parser.parse_args()

    input_file = pathlib.Path(args.dataset_file).absolute()
    if input_file.is_file():  # Check the input file existence and format
        output_path = pathlib.Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)  # Create directory if not exists for output
        logging.info(msg='Starting process...')
        ds = pq.ParquetDataset(input_file, use_legacy_dataset=False)  # Read dataset or file
        files = ds.files

        similar = SimilarEmbedding(1)  # Init with
        data = pq.read_table(files[0])  #
        if args.limit:
            data = data.slice(length=args.limit)

        dict_data = data.to_pydict()
        mask = [similar(row) for row in zip(*dict_data.values())]
        cleaned = data.filter(mask)
        pq.write_table(cleaned, Path(args.output).absolute())
        logging.info(
            msg=f'Completed successfully. Reduced {mask.count(False)} out of {len(mask)} rows. \nResult saved to '
                f'{Path(args.output).absolute()}')
    else:
        logging.info(msg='Input file is not exists')
