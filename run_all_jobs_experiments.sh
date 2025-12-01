#!/bin/bash

echo "Submitting all SLURM jobs from the 'jobs/' directory..."

for job_script in experiments/jobs/job_*.sh; do
    echo "Submitting $job_script"
    sbatch "$job_script"
done