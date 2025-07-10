#!/usr/bin/env python3

from pathlib import Path
import hyp3_sdk as sdk
from dateutil.parser import parse as parse_date
import asf_search as asf
import pandas as pd
import sys

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: submit_burst.py job_name max_temp_base_days submit_true seasonal_true")
        sys.exit(1)

## Stack input arguments
#stack_start = parse_date('2014-10-01 00:00:00Z')
#stack_end = parse_date('2025-06-06 00:00:00Z')
stack_start = parse_date('2014-06-01 00:00:00Z')
stack_end = parse_date('2025-07-01 00:00:00Z')
max_temporal_baseline = int(sys.argv[2]) #days
jname = sys.argv[1]

## Stack search parameters from ASF Vertex
options = {
	'intersectsWith': 'POLYGON((-113.9133 39.7297,-113.8866 39.7297,-113.8866 39.7409,-113.9133 39.7409,-113.9133 39.7297))',
	'dataset': 'SLC-BURST',
	'flightDirection': 'Descending',
	'maxResults': 1000
}

## Search via ASF 
search_results = asf.search(**options)

## SBAS search
baseline_results = asf.baseline_search.stack_from_product(search_results[-1])

## Extract properties and filter by starting/ending dates
columns = list(baseline_results[0].properties.keys()) + ['geometry', ]
data = [list(scene.properties.values()) + [scene.geometry, ] for scene in baseline_results]

stack = pd.DataFrame(data, columns=columns)
stack['startTime'] = stack.startTime.apply(parse_date)

stack = stack.loc[(stack_start <= stack.startTime) & (stack.startTime <= stack_end)]

sbas_pairs = set()

## Filter all possible pairs by chosen temporal baseline
for reference, rt in stack.loc[::-1, ['sceneName', 'temporalBaseline']].itertuples(index=False):
    print("scene name is ", reference, " temporal baseline is", rt)
    secondaries = stack.loc[
        (stack.sceneName != reference)
        & (stack.temporalBaseline - rt <= (max_temporal_baseline))
        & (stack.temporalBaseline - rt > 0)
    ]
    for secondary in secondaries.sceneName:
        sbas_pairs.add((reference, secondary))

## If seasonal search True, find year-long pairs between August and December
if sys.argv[4] == 'True':
    for d1, reference, rt in stack.loc[::-1, ['startTime','sceneName', 'temporalBaseline']].itertuples(index=False):
        month = d1.month
        #if month > 8 and month < 12:
        if month < 9:
            print("scene name is ", reference, " temporal baseline is", rt)
            secondaries = stack.loc[
                (stack.sceneName != reference)
                & (stack.temporalBaseline - rt <= (max_temporal_baseline + 365))
                & (stack.temporalBaseline - rt > 365)
            ]
            for secondary in secondaries.sceneName:
                sbas_pairs.add((reference, secondary))


## Sort final pairs and save to a text file

sorted_sbas_pairs = sorted(sbas_pairs)

with open(f'{jname}_pairs.txt', 'w') as file:
    for reference, secondary in sorted_sbas_pairs:
        file.write(f"{reference},{secondary}\n")

print(len(sbas_pairs))

## If submit is True, submit job using Hyp3
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