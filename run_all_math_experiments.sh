#!/bin/bash

echo "Submitting all SLURM jobs from the 'math/' directory..."

for job_script in math/job_*.sh; do
    echo "Submitting $job_script"
    sbatch "$job_script"
done