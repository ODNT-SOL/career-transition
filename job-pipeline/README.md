# Job Pipeline Cron Setup

## Manual Run
```bash
cd /home/chronos/career-transition/job-pipeline
./run.sh
```

## Daily Cron (run at 6 AM)
```bash
0 6 * * * /home/chronos/career-transition/job-pipeline/run.sh >> /home/chronos/career-transition/job-pipeline/cron.log 2>&1
```

Add via: `crontab -e`