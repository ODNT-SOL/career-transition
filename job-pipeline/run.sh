#!/bin/bash
# Job Pipeline run script

cd /home/chronos/career-transition/job-pipeline

# Run the job search
/home/chronos/career-transition/.venv/bin/python job_search.py --config config.json

echo "Job search completed at $(date)"