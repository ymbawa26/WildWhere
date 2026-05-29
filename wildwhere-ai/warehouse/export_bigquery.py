import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from warehouse.export_sqlite import EXPORT_TABLES


REQUIRED_ENV = ["GOOGLE_APPLICATION_CREDENTIALS", "BIGQUERY_PROJECT_ID", "BIGQUERY_DATASET"]


def export_bigquery() -> dict:
    missing = [key for key in REQUIRED_ENV if not os.getenv(key)]
    if missing:
        message = f"BigQuery export skipped. Missing environment variables: {', '.join(missing)}"
        print(message)
        return {"status": "skipped", "missing": missing}
    try:
        from google.cloud import bigquery
    except ImportError:
        message = "BigQuery export skipped. Install google-cloud-bigquery to enable this exporter."
        print(message)
        return {"status": "skipped", "missing_package": "google-cloud-bigquery"}

    project_id = os.environ["BIGQUERY_PROJECT_ID"]
    dataset = os.environ["BIGQUERY_DATASET"]
    client = bigquery.Client(project=project_id)
    loaded = []
    for table_name, path in EXPORT_TABLES.items():
        if not path.exists():
            continue
        df = pd.read_csv(path)
        table_id = f"{project_id}.{dataset}.{table_name}"
        job = client.load_table_from_dataframe(df, table_id, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))
        job.result()
        loaded.append(table_id)
    print({"status": "ok", "loaded": loaded})
    return {"status": "ok", "loaded": loaded}


if __name__ == "__main__":
    export_bigquery()
