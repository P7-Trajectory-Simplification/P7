#!/bin/bash

echo "Submitting all SLURM jobs from the 'experiments/math/' directory..."

for job_script in experiments/math/job_*.sh; do
    echo "Submitting $job_script"
    sbatch "$job_script"
done