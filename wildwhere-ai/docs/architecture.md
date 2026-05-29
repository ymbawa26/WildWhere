# WildWhere AI Architecture

WildWhere AI begins as a small but extensible data platform. Step 1 focuses on source acquisition, validation, and durable local storage. The architecture intentionally separates raw data collection from future processing and modeling work.

## Current Step 1 Flow

1. Acquisition scripts collect or prepare source-aligned CSV files in `data/raw/`.
2. `validate_downloads.py` verifies file existence, required columns, and non-empty extracts.
3. `database/init_db.py` creates `wildwhere.db` from `schema.sql`.
4. Pytest tests validate raw data integrity and database initialization.

## Design Principles

- Raw data is preserved separately from future transformed data.
- Shared configuration lives in `config/settings.py`.
- Database schema uses explicit primary keys and foreign keys.
- Scripts fail loudly when required data is missing or malformed.
- Future ETL work should write to `data/processed/` before loading analytics tables.

## Future Architecture Direction

Later phases should add a formal ETL layer, processed feature tables, model training modules, dashboard services, and CI checks. The first production-quality milestone should be a reproducible command path that rebuilds raw extracts, processed tables, tests, and the dashboard from a clean checkout.
