from pathlib import Path
import numpy as np
from copy import deepcopy
from datetime import datetime
from dateutil.relativedelta import relativedelta

folder = '/content/mnt/MyDrive/SAR/Backup/p100/data_1202'#'/content/mnt/MyDrive/SAR/Backup/milford_2014_2021/data'
data_dir=Path(folder)

jname = 'p100_2022_2024_north_gaps'
job_specification = {
    "job_parameters": {'apply_water_mask': True, 'include_dem': True, 'include_displacement_maps': False, 'include_inc_map': True, 'include_look_vectors': True, 'include_los_displacement': False, 'include_wrapped_phase': True, 'looks': '20x4', 'phase_filter_parameter': 0.4},
    "job_type": "INSAR_GAMMA",
    "name": jname,
}

#Download pairs from scene IDs

import asf_search as asf

options = {
	'intersectsWith': 'POLYGON((-109.3264 37.1596,-108.8806 37.1596,-108.8806 40.2389,-109.3264 40.2389,-109.3264 37.1596))',
	'dataset': 'SENTINEL-1',
	'start': '2022-05-01T06:00:00Z',
	'end': '2024-12-02T05:59:59Z',
	'relativeOrbit': 129,
	'processingLevel': 'SLC',
	'season': [
		'121',
		'335'
	],
	'maxResults': 250
}

results = asf.search(**options)
print(len(results))


jobs = []

job = deepcopy(job_specification)

perpt_max = 40
perpt_max_yrlong = 55

results_r = results[::-1]

for c, ref in enumerate(results_r):
  start = datetime.strptime(ref.properties['startTime'],'%Y-%m-%dT%H:%M:%SZ')
  stacks = ref.stack()
  day = (12 - (start.month - 8))*30
  print(start.month)
  print(day)
  for d, sec in enumerate(stacks):
    start_sec = datetime.strptime(sec.properties['startTime'],'%Y-%m-%dT%H:%M:%SZ')
    #same-year intfs
    if sec.properties['temporalBaseline'] > 0 and sec.properties['temporalBaseline'] < perpt_max: #and start_sec < datetime.strptime('2022-07-10T00:00:00Z','%Y-%m-%dT%H:%M:%SZ'):
      print(ref.properties['sceneName'])
      print(sec.properties['sceneName'])
      print(sec.properties['temporalBaseline'])
      job = deepcopy(job_specification)
      job['job_parameters']['granules'] = [ref.properties['sceneName'], sec.properties['sceneName']]
      jobs.append(job)
    #year-long intfs
    if start.month > 7 and start.month < 11:
      if sec.properties['temporalBaseline'] > day and sec.properties['temporalBaseline'] < (day + perpt_max_yrlong):
        print(ref.properties['sceneName'])
        print(sec.properties['sceneName'])
        print(sec.properties['temporalBaseline'])
        job = deepcopy(job_specification)
        job['job_parameters']['granules'] = [ref.properties['sceneName'], sec.properties['sceneName']]
        jobs.append(job)

print(f'{len(jobs)} jobs')

hyp3 = HyP3(prompt=True)

hyp3.submit_prepared_jobs(jobs)


hyp3 = HyP3(prompt=True)

jobs = []

job = deepcopy(job_specification)
job['job_parameters']['granules'] = ["S1A_IW_SLC__1SDV_20220620T133353_20220620T133421_043747_05391A_53CD", "S1A_IW_SLC__1SDV_20220807T133413_20220807T133440_044447_054DDC_D4F8"]
jobs.append(job)

print(f'Submitting {len(jobs)} jobs')

hyp3.submit_prepared_jobs(jobs)