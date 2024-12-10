#!/usr/bin/env python

import hyp3_sdk as sdk
from pathlib import Path
import dask
from dask.distributed import Client, progress


if __name__ == '__main__':
    #! Chaotic because zip file is deleted after unzipped, some workesr can't recognize this?
    client = Client(threads_per_worker=2, n_workers=1)
    print(client.dashboard_link)

results = []
folder = '/home/tshreve/sar/mintpy/hyp3/p129_merged/data_asf'
data_dir=Path(folder)

for ii in data_dir.glob('*.zip'):
    print(ii)
    try:
        result = dask.delayed(sdk.util.extract_zipped_product)(ii)
        results.append(result)
    except Exception as e:
        print(f'Warning: {e} Skipping download for {ii}.')

futures = dask.persist(*results)
results = dask.compute(*futures)