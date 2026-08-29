"""
generate_logs.py
Generates a synthetic dataset of data-pipeline job runs.
Nothing here is real company data — it's all made up so you can safely
practice on your own laptop.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)  # so the data is reproducible while you're testing

JOB_NAMES = [
    "customer_orders_ingest",
    "daily_sales_aggregate",
    "inventory_sync",
    "user_events_etl",
    "finance_reconciliation",
    "marketing_attribution_load",
    "product_catalog_refresh",
    "shipment_tracking_sync",
    "clickstream_dedupe",
    "warehouse_stock_snapshot",
]

STATUSES = ["SUCCESS", "SUCCESS", "SUCCESS", "FAILED", "FAILED", "WARNING"]

ERROR_MESSAGES = {
    "FAILED": [
        "Connection timeout to source database after 30s",
        "Schema mismatch: expected column 'order_id' not found",
        "Out of memory error during shuffle stage",
        "Upstream table 'raw_events' was empty at run time",
        "Authentication failed for service principal",
        "Duplicate primary key violation on merge",
    ],
    "WARNING": [
        "Row count 15% lower than 7-day average",
        "3 records skipped due to null values in required field",
        "Job completed but ran 2.5x longer than usual",
        "Partition skew detected on 'region' column",
    ],
    "SUCCESS": [""],
}


def generate_logs(num_days=30, jobs_per_day=10):
    rows = []
    start_date = datetime(2026, 7, 1)

    for day in range(num_days):
        run_date = start_date + timedelta(days=day)
        for _ in range(jobs_per_day):
            job_name = random.choice(JOB_NAMES)
            status = random.choice(STATUSES)
            error_message = random.choice(ERROR_MESSAGES[status])
            duration_minutes = round(random.uniform(2, 45), 1)
            rows_processed = random.randint(1000, 500000)

            run_time = run_date + timedelta(
                hours=random.randint(0, 23), minutes=random.randint(0, 59)
            )

            rows.append(
                {
                    "run_id": f"{job_name}_{run_time.strftime('%Y%m%d_%H%M')}",
                    "job_name": job_name,
                    "run_timestamp": run_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": status,
                    "duration_minutes": duration_minutes,
                    "rows_processed": rows_processed,
                    "error_message": error_message,
                }
            )

    return rows


def write_csv(rows, path="pipeline_logs.csv"):
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic log rows to {path}")


if __name__ == "__main__":
    logs = generate_logs(num_days=30, jobs_per_day=10)
    write_csv(logs, "pipeline_logs.csv")