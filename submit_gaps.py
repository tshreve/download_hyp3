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
        print("Usage: submit_gaps.py ref_scene_ID sec_scene_ID job_name [filter_strength]")
        sys.exit(1)
    elif len(sys.argv) == 4:
        filt = 0.4
    elif len(sys.argv) == 5: 
        filt = float(sys.argv[4])


# parallel processing works well with username and password input here
# could also try adding credentials from a `.netrc` file.

hyp3 = HyP3(prompt=True)


jname = sys.argv[3]
jobs = []

job_specification = {
    "job_parameters": {'apply_water_mask': True, 'include_dem': True, 'include_displacement_maps': False, 'include_inc_map': True, 'include_look_vectors': True, 'include_los_displacement': False, 'include_wrapped_phase': True, 'looks': '20x4', 'phase_filter_parameter': filt},
    "job_type": "INSAR_GAMMA",
    "name": jname,
}

job = deepcopy(job_specification)
job['job_parameters']['granules'] = [sys.argv[1], sys.argv[2]]
jobs.append(job)

hyp3.submit_prepared_jobs(jobs)