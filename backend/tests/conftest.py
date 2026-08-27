import os
import pytest
import database


@pytest.fixture
def test_database():
    database.DATABASE_PATH = 'test_expenses.db'
    database.create_tables()

    yield

    if os.path.exists('test_expenses.db'):
        os.remove('test_expenses.db')

    database.DATABASE_PATH = 'expenses.db'