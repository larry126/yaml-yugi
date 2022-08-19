# SPDX-FileCopyrightText: © 2022 Kevin Lu
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from math import ceil
from multiprocessing import Pool
import os
import sys

from ruamel.yaml import YAML

from job import job


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path/to/wikitexts> [path/to/zh-CN]")
    wikitext_dir = sys.argv[1]
    zh_cn_dir = sys.argv[2] if len(sys.argv) > 2 else None
    yaml = YAML()
    yaml.width = sys.maxsize

    files = []
    skip = True
    for filename in os.listdir(wikitext_dir):
        # if skip:
        #     if filename == "256277.yaml":
        #         skip = False
        #     else:
        #         continue
        if os.path.isfile(os.path.join(wikitext_dir, filename)):
            files.append(filename)

    processes = os.cpu_count()
    size = ceil(len(files) / processes)
    partitions = [files[i:i+size] for i in range(0, len(files), size)]
    with Pool(os.cpu_count() * 2) as pool:
        jobs = [
            pool.apply_async(job, (yaml, wikitext_dir, zh_cn_dir, partition))
            for partition in partitions
        ]
        for result in jobs:
            result.get()


if __name__ == "__main__":
    main()
