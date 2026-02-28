from pathlib import Path


def test_schema_sql_exists() -> None:
    schema_path = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"
    assert schema_path.exists()
