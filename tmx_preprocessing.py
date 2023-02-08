import argparse
import asyncio
import logging
import pathlib
from multiprocessing import cpu_count

from src import TMXCleaner

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract and clean segments from TMX file')
    parser.add_argument('--tmx-file', type=str, required=True, help='Path to TMX file')
    parser.add_argument('--output', type=str, required=True, help='Path to output file')
    parser.add_argument('--processes', type=str, required=False,
                        help='Amount of processes to start. Default equals to the amount of CPU', default=cpu_count())
    parser.add_argument('--chunk-size', type=int, required=False,
                        help='Amount of rows to process and save.', default=100000)
    args = parser.parse_args()

    input_file = pathlib.Path(args.tmx_file)
    if input_file.is_file() and input_file.name.endswith('.tmx'): # Check the input file existence and format
        output_path = pathlib.Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True) # Create directory if not exists for output
        logging.info(msg='Starting process...')
        event_loop = asyncio.get_event_loop()
        tmx_cleaner = TMXCleaner(args.tmx_file, args.output, args.processes, args.chunk_size)
        event_loop.run_until_complete(tmx_cleaner.run())
        logging.info(msg='Completed successfully')
    else:
        logging.info(msg='Input file is not exists or is in wrong format')
