# snow-radar
Code to process FMCW radargrams collected over snowpack for snow depth. Surface and ground returns are semi-automatically picked using a wavelet transform image analysis techniques that traces high gradient contrast features. The main processing code is contained in the scripts that begin with "01", "02", "03". There are additional scripts to prepare the data for submission to NSIDC and to work with ancilliary datasets (e.g., lidar and probe data collected in field campaigns). 

![drift_fig](https://github.com/user-attachments/assets/190b9384-42f0-43bb-9478-ed62e673f99c)


## Environment
#### For Boise State Borah users:
The environment is on Borah as an apptainer container under **/cm/shared/containers/autoterm.sif**. To run the Jupyter Notebooks on Borah OnDemand, use

```
module load apptainer/1.2.5
apptainer run /cm/shared/containers/autoterm.sif jupyter notebook
```

#### For other users:
The environment is available as a docker container on DockerHub, retrievable using:

```
docker pull jukesliu/autoterm:autoterm
```

## Workflow for picking snow depths from FMCW radar outputs:
The three main scripts used are **01_calibrate_radargrams.ipynb**, **02_process_radargrams_wtmm.py**, and **03_clean_WTMM_radar_picks.ipynb**. 01 and 03 are interactive and therefore must be run as Jupyter notebooks (on Borah OnDemand for Boise State users). 02 can be run on Borah as jobs or on a local machine using the .ipynb version.

* 01_calibrate_radargrams.ipynb (Borah OnDemand)
* 02_process_radagrams_wtmm.py (Borah)
* 03_clean_WTMM_radar_picks.ipynb (Borah OnDemand)

The only input needed to start the first script is a folder containing the .mat files of the FMCW radar ouput containing the geolocated data with sky calibration (skycal) indexes. The last script **03_clean_WTMM_radar_picks.ipynb** uses widget interactive tools to iteratively filter and clean up the semi-automated snow depth picks.

## For Boise State Borah users: running 02_process_radargrams_wtmm.py on Borah
Adjust the 3 input paths in **test-slurm.sh** to match the path to the **02_process_radargrams_wtmm.py** script in Borah, the folder containing FMCW radar ouput on Borah, and the desired output file folder on Borah. Then, you can run a single job with test parameters. For Reynold's mountain, the best parameters were 800 (pixels) for the Isurf threshold, 1000 (pixels) for the wavelet spatial scale, 100 (pixels) for the length threshold, and 1 for the mean gradient value threshold.
```
sbatch test-slurm.sh 800 1000 100 1
```

To test different parameters, use **test-slurm-loop.sh** which calls **test-slurm.sh** and loops through a list of wavelet spatial scales {start...end...interval} and list of length thresholds and runs each as its own Borah job. The first input argument is the Isurf threshold, the maximum depth (in pixels) for the snow surface pick. Adjust this value for new sites. The last input argument is the mean gradient value threshold for filtering out other delineations (e.g., along internal interfaces in the snowpack, which should be less bright), this is kept constant at 1. 
