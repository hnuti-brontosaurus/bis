import pytest
from django.db import connection


@pytest.fixture(autouse=True)
def reset_sequences(db):
    """Reset sequences whose starting value may conflict with migration-inserted explicit IDs."""
    tables = ["donations_fundraisingcampaign"]
    with connection.cursor() as cursor:
        for table in tables:
            cursor.execute(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f'GREATEST(MAX(id), 1), true) FROM "{table}"'
            )
