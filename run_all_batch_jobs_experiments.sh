#!/bin/bash

echo "Submitting all SLURM jobs from the 'jobs/' directory..."

for job_script in experiments/jobs/job_*_DP.sh; do
    echo "Submitting $job_script"
    sbatch "$job_script"
done