#!/bin/bash

echo "Submitting all SLURM jobs from the 'math/' directory..."

for job_script in experiments/results/math_comparison/experiments/job_*.sh; do
    echo "Submitting $job_script"
    sbatch "$job_script"
done