import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from warehouse.export_sqlite import EXPORT_TABLES


REQUIRED_ENV = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]


def export_snowflake() -> dict:
    missing = [key for key in REQUIRED_ENV if not os.getenv(key)]
    if missing:
        message = f"Snowflake export skipped. Missing environment variables: {', '.join(missing)}"
        print(message)
        return {"status": "skipped", "missing": missing}
    try:
        import snowflake.connector
        from snowflake.connector.pandas_tools import write_pandas
    except ImportError:
        message = "Snowflake export skipped. Install snowflake-connector-python[pandas] to enable this exporter."
        print(message)
        return {"status": "skipped", "missing_package": "snowflake-connector-python"}

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )
    loaded = []
    try:
        for table_name, path in EXPORT_TABLES.items():
            if not path.exists():
                continue
            df = pd.read_csv(path)
            success, _, rows, _ = write_pandas(conn, df, table_name.upper(), auto_create_table=True, overwrite=True)
            loaded.append({"table": table_name, "rows": rows, "success": success})
    finally:
        conn.close()
    print({"status": "ok", "loaded": loaded})
    return {"status": "ok", "loaded": loaded}


if __name__ == "__main__":
    export_snowflake()
