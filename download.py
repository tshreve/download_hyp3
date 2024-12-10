#!/usr/bin/env python

from pathlib import Path
import numpy as np
from hyp3_sdk import HyP3
from dask.distributed import Client

if __name__ == '__main__':
    client = Client(threads_per_worker=2, n_workers=5)
    print(client.dashboard_link)

folder = '/home/tshreve/sar/mintpy/hyp3/p129_merged/data_asf'

hyp3 = HyP3(username='tshreve14',password='T17a15g50')

jname = 'p129_2022_2024'

job = hyp3.find_jobs(name=jname)
#job = hyp3.watch(job)
insar_products = job.download_files(folder)