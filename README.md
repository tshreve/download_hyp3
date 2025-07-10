# download_hyp3
This package is for submitting, downloading and unzipping Sentinel-1 interferograms from Alaska Satellite Facility's Hybrid Pluggable Processing Pipeline (HyP3). 
## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

- ## Installation
1. Clone the repository:
```bash
git clone https://github.com/tshreve/download_hyp3.git
```

2. Install dependencies using *download_hyp3_dependencies.txt* in a conda environment:
```bash
echo 'dask
hyp3_sdk
asf_search
numpy' > download_hyp3_dependencies.txt
 ```

```bash
conda create --name prep_hyp3 --file download_hyp3_dependencies.txt
 ```

## Usage
To run, use the following commands:  <br>
1a.  <br>
```bash
./submit.py job_name max_temp_base_days submit_true [filter_strength]
```

where: <br>
```job_name``` : HyP3 job name <br>
```max_temp_base_days``` : maximum temporal baseline for nearest neighbor pairs  <br>
```submit_true```: True to submit job; False to only create text file with pair names <br>
```filter_strength``` : interferogram filter strength <br>
 <br>

 1b.  <br>
 ```bash
./submit_gaps.py ref_scene_ID sec_scene_ID job_name [filter_strength]
```

where: <br>
```ref_Scene_ID``` : Reference scene ID <br>
```sec_Scene_ID``` : Secondary scene ID   <br>
```job_name```: HyP3 job name <br>
```filter_strength``` : interferogram filter strength <br>
 <br>

______ <br>
OR <br>
______ <br>

To submit individual bursts, use: <br>
 ```bash
./submit_burst.py job_name max_temp_base_days submit_true seasonal_true
```

To submit area spanning multiple bursts (up to 15 bursts can be stitched together using ```hyp3_sdk```'s ```submit_insar_isce_multi_burst_job```), use: <br>
 ```bash
./submit_multiburst.py job_name max_temp_base_days submit_true seasonal_true
```

where: <br>
```job_name``` : HyP3 job name <br>
```max_temp_base_days``` : maximum temporal baseline for nearest neighbor pairs  <br>
```submit_true```: True to submit job; False to only create text file with pair names <br>
```seasonal_true``` : True to include year-long interferograms; False to only include nearest neighbor interferograms <br>
 <br>



 2.  <br>
```bash
./download.py  data_folder job_name
```

where: <br>
```data_folder``` : folder to download data <br>
```job_name``` : HyP3 job name <br>
 <br>
 3.  <br>
```bash
./unzip.py  data_folder
```

where: <br>
```data_folder``` : folder to download data <br>

## Contributing
Contributions are encouraged! I will do my best to continue updating this script, but if you've found ways to improve it on your own, feel free to create a PR using the following:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes.
4. Push your branch: `git push origin feature-name`.
5. Create a pull request.

Ideas for increased functionality are also welcome. Thanks to all who are helping to make InSAR more accessible!


