#!/bin/bash

#SBATCH --job-name=prenacs_job_array
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
#SBATCH --constraint=scratch
#SBATCH --qos=short
#SBATCH --mail-type=ALL

PLUGIN_FILE=$1
PARAMETERS_FILE=$2
INPUT_LIST_FILE=$3
OUTPUT_DIR=$4


module purge
eval "$(/usr/users/kanbertay/software/miniconda3/bin/conda shell.bash hook)"
conda activate prenacs_slurm_env

# TODO: Get the "prenacs-array-task" path without user input
~/software/prenacs/prenacs/prenacs-array-task \
 $PLUGIN_FILE $PARAMETERS_FILE \
 $INPUT_LIST_FILE $SLURM_ARRAY_TASK_ID \
 $OUTPUT_DIR
