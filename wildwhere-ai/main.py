from acquisition.validate_downloads import validate_all_downloads
from database.init_db import initialize_database


def main() -> None:
    print("Validating raw WildWhere AI datasets...")
    validate_all_downloads()
    print("Building SQLite database...")
    initialize_database()
    print("Step 1 pipeline completed successfully.")


if __name__ == "__main__":
    main()
