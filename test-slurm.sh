#!/bin/bash
#SBATCH -J test       # job name
#SBATCH -o log_slurm.o%j  # output and error file name (%j expands to jobID)
#SBATCH -n 1              # total number of tasks requested
#SBATCH -c 1             # CPU cores per task
#SBATCH -N 1              # number of nodes you want to run on
#SBATCH -p bsudfq         # queue (partition)
#SBATCH -t 36:00:00       # run time (hh:mm:ss) - 12.0 hours in this example.
#SBATCH --mail-user jukesliu@u.boisestate.edu
#SBATCH --mail-type all

# Activate the environment
# Replace environmentName with your environment name
#. ~/.bashrc
#conda activate autoterm_env
# eventually: activate apptainer container  
module load apptainer/1.2.5

# Your code goes here
# run processes script with the following inputs:
# 1) path to the folder with the stitched radargram.npy and x and y coordinates.npy
# 2) path to the output folder
# 3) Isurf_thresh: integer index number with the maximum index (depth in pixels) of the surface return (e.g., 200)
# 4) wtmm_scale: spatial scale to run the wavelet transform [in pixels] (e.g., 1000)
# 5) size_thresh: minimum length threshold to filter the wavelet output traces [in pixels] (e.g., 200)
# 6) mod_thresh_multiplier: minimum modulus value as a fraction of the mean throughout the image (e.g., 1 = mean, 1.5 = 150% of the mean, 0.8 = 80% of the mean)
apptainer run /cm/shared/containers/autoterm.sif python3 /bsuhome/jukesliu/Documents/GitHub/snow-radar/snow-radar/02_process_radargrams_wtmm.py /bsushare/hpmarshall-shared/FMCW-radar/GM2020/FMCW_processed/ /bsushare/hpmarshall-shared/FMCW-radar/GM2020/FMCW_wavelet_processed/ $1 $2 $3 $4
