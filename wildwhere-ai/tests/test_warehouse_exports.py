import importlib


def test_warehouse_export_modules_import_without_credentials():
    for module_name in [
        "warehouse.export_sqlite",
        "warehouse.export_bigquery",
        "warehouse.export_snowflake",
    ]:
        importlib.import_module(module_name)
