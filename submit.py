#!/usr/bin/env python3

from pathlib import Path
import numpy as np
from copy import deepcopy
from datetime import datetime
from dateutil.relativedelta import relativedelta
import asf_search as asf
from hyp3_sdk import HyP3
import sys

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: submit.py job_name max_temp_base_days submit_true [filter_strength]")
        sys.exit(1)
    elif len(sys.argv) == 4:
        filt = 0.4
    elif len(sys.argv) == 5: 
        filt = float(sys.argv[4])
  

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# define job parameters
jname = sys.argv[1] #p93_desc_2014_2017

job_specification = {
    "job_parameters": {'apply_water_mask': True, 'include_dem': True, 'include_displacement_maps': False, 'include_inc_map': True, 'include_look_vectors': True, 'include_los_displacement': False, 'include_wrapped_phase': True, 'looks': '20x4', 'phase_filter_parameter': filt},
    "job_type": "INSAR_GAMMA",
    "name": jname,
}

# search images available (seasonal search)
options = {
	'intersectsWith': 'POLYGON((-113.8789 37.5667,-113.4477 37.5667,-113.4477 37.9314,-113.8789 37.9314,-113.8789 37.5667))',
	'dataset': 'SENTINEL-1',
	'start': '2017-03-11T06:00:00Z',
	'end': '2024-12-11T06:59:59Z',
	'relativeOrbit': 93,
	'processingLevel': 'SLC',
	'flightDirection': 'Ascending',
	'season': [
		'121',
		'335'
	],
	'maxResults': 250
}

# search for scenes
results = asf.search(**options)
print(len(results))

# prepare job list
jobs = []
job = deepcopy(job_specification)

# set temporal baseline constraints for nearest neighbor and year-long interferograms
perpt_max = int(sys.argv[2])
perpt_max_yrlong = 43
results_r = results[::-1]

# find pairs for each scene (nearest neighbor and year-long pairs) and write pairs and temporal baselines to file for double-checking
with open(f'{jname}_pairs.txt', 'w') as file:
  for c, ref in enumerate(results_r):
    start = datetime.strptime(ref.properties['startTime'],'%Y-%m-%dT%H:%M:%SZ')
    stacks = ref.stack()
    day = (12 - (start.month - 8))*30
    file.write(f"Month is {months[start.month-1]} \n")
    file.write(f"Julian day is {day}\n")
    for d, sec in enumerate(stacks):
      start_sec = datetime.strptime(sec.properties['startTime'],'%Y-%m-%dT%H:%M:%SZ')
      # same-year intfs
      if sec.properties['temporalBaseline'] > 0 and sec.properties['temporalBaseline'] < perpt_max: #and start_sec < datetime.strptime('2022-07-10T00:00:00Z','%Y-%m-%dT%H:%M:%SZ'):
        file.write(ref.properties['sceneName']+' \n')
        file.write(sec.properties['sceneName']+' \n')
        file.write(str(sec.properties['temporalBaseline'])+' \n')
        job = deepcopy(job_specification)
        job['job_parameters']['granules'] = [ref.properties['sceneName'], sec.properties['sceneName']]
        jobs.append(job)
      # year-long intfs
      if start.month > 7 and start.month < 11:
        if sec.properties['temporalBaseline'] > day and sec.properties['temporalBaseline'] < (day + perpt_max_yrlong):
          file.write(ref.properties['sceneName']+' \n')
          file.write(sec.properties['sceneName']+' \n')
          file.write(str(sec.properties['temporalBaseline'])+' \n')
          job = deepcopy(job_specification)
          job['job_parameters']['granules'] = [ref.properties['sceneName'], sec.properties['sceneName']]
          jobs.append(job)

# submit all jobs
print(f'{len(jobs)} jobs')
if sys.argv[3] == 'True':
  hyp3 = HyP3(prompt=True)

  # May need to split up job submission if too many jobs
  # Could add a try/except statement to catch errors
  hyp3.submit_prepared_jobs(jobs[0:100])
  #hyp3.submit_prepared_jobs(jobs[101:200])
  #hyp3.submit_prepared_jobs(jobs[201:300])
  #hyp3.submit_prepared_jobs(jobs[301:400])