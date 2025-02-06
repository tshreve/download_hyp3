#!/usr/bin/env python3

from pathlib import Path
import hyp3_sdk as sdk
from dateutil.parser import parse as parse_date
import asf_search as asf
import pandas as pd
import sys

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: submit.py job_name max_temp_base_days submit_true seasonal_true")
        sys.exit(1)


stack_start = parse_date('2014-05-01 00:00:00Z')
stack_end = parse_date('2025-01-31 00:00:00Z')
max_temporal_baseline = int(sys.argv[2]) #days
jname = sys.argv[1]

options = {
	'intersectsWith': 'POLYGON((-111.8901 40.9843,-111.848 40.9843,-111.848 41.0272,-111.8901 41.0272,-111.8901 40.9843))',
	'dataset': 'SLC-BURST',
	'start': '2014-06-14T06:00:00Z',
	'end': '2025-02-01T06:59:59Z',
	'relativeOrbit': 100,
	'maxResults': 5000
}
search_results = asf.search(**options)

baseline_results = asf.baseline_search.stack_from_product(search_results[-1])

columns = list(baseline_results[0].properties.keys()) + ['geometry', ]
data = [list(scene.properties.values()) + [scene.geometry, ] for scene in baseline_results]

stack = pd.DataFrame(data, columns=columns)
stack['startTime'] = stack.startTime.apply(parse_date)

stack = stack.loc[(stack_start <= stack.startTime) & (stack.startTime <= stack_end)]

sbas_pairs = set()

for reference, rt in stack.loc[::-1, ['sceneName', 'temporalBaseline']].itertuples(index=False):
    print("scene name is ", reference, " temporal baseline is", rt)
    secondaries = stack.loc[
        (stack.sceneName != reference)
        & (stack.temporalBaseline - rt <= (max_temporal_baseline))
        & (stack.temporalBaseline - rt > 0)
    ]
    for secondary in secondaries.sceneName:
        sbas_pairs.add((reference, secondary))

if sys.argv[4] == 'True':
    for reference, rt in stack.loc[::-1, ['sceneName', 'temporalBaseline']].itertuples(index=False):
        print("scene name is ", reference, " temporal baseline is", rt)
        secondaries = stack.loc[
            (stack.sceneName != reference)
            & (stack.temporalBaseline - rt <= (max_temporal_baseline + 365))
            & (stack.temporalBaseline - rt > 365)
        ]
        for secondary in secondaries.sceneName:
            sbas_pairs.add((reference, secondary))


sorted_sbas_pairs = sorted(sbas_pairs)

with open(f'{jname}_pairs.txt', 'w') as file:
    for reference, secondary in sorted_sbas_pairs:
        file.write(f"{reference},{secondary}\n")

print(len(sbas_pairs))

if sys.argv[3] == 'True':
    
    hyp3 = sdk.HyP3(prompt=True)
    jobs = sdk.Batch()
    for reference, secondary in sbas_pairs:
        jobs += hyp3.submit_insar_isce_burst_job(
            granule1 = reference,
            granule2 = secondary, 
            apply_water_mask = True,
            name = jname,
            looks = '10x2'
        )
    print("Submitting jobs")