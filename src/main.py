# SPDX-FileCopyrightText: © 2022 Kevin Lu
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from argparse import ArgumentParser
import logging
import math
import os

from job import job


parser = ArgumentParser()
parser.add_argument("wikitext_directory", help="yaml-yugipedia card texts")
parser.add_argument("--assignments", help="fake password assignment YAML")
parser.add_argument("--zh-CN", help="yaml-yugi-zh card texts")
parser.add_argument("--ko", help="yaml-yugi-ko TBD")
parser.add_argument("--generate-schema", action="store_true", help="output generated JSON schema file")
parser.add_argument("--processes", type=int, default=0, help="number of worker processes, default ncpu")

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    processes = args.processes
    if processes == 0:
        processes = os.cpu_count()
        logger.info(f"Using {processes} processes.")

    files = [
        filename for filename in
        os.listdir(args.wikitext_directory)
        if os.path.isfile(os.path.join(args.wikitext_directory, filename))
    ]

    if processes == 1:
        job(args.wikitext_directory, files, args.zh_CN, args.assignments)
    else:
        size = math.ceil(len(files) / processes)
        partitions = [files[i:i+size] for i in range(0, len(files), size)]

        from multiprocessing import Pool
        with Pool(processes) as pool:
            jobs = [
                pool.apply_async(job, (args.wikitext_directory, partition, args.zh_CN, args.assignments))
                for partition in partitions
            ]
            for result in jobs:
                result.get()


if __name__ == "__main__":
    main()
