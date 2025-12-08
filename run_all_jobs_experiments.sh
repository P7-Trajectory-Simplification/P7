#!/bin/bash

echo "Submitting all SLURM jobs from the 'algorithm_comp/' directory..."

for job_script in experiments/results/algorithm_comparison/experiments/job_*.sh; do
    echo "Submitting $job_script"
    sbatch "$job_script"
done