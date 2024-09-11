import piccolo.table
import pytest
from litestar.status_codes import HTTP_200_OK
from litestar.testing import TestClient

from app import app
from lipotes.collection.tables import Collection, LexemeCollection
from lipotes.dictionary.tables import Lexeme


@pytest.fixture()
def setup_db():
    tables = [Lexeme, Collection, LexemeCollection]
    piccolo.table.create_db_tables_sync(*tables)
    yield
    piccolo.table.drop_db_tables_sync(*tables)


@pytest.fixture()
def client(setup_db):
    with TestClient(app=app) as client:
        yield client


def test_hello(client):
    response = client.get("/api/v1/")
    assert response.status_code == HTTP_200_OK
