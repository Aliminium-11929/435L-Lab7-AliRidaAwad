"""Lab 7: isolated database and Flask API tests for the Lab 5 project."""
import runpy
import sqlite3
from pathlib import Path

import pytest

import db
from app import app


@pytest.fixture
def database(tmp_path, monkeypatch):
    """Use a fresh directory so the real database is never modified."""
    monkeypatch.chdir(tmp_path)
    db.initialize_database()
    return tmp_path / 'database.db'


@pytest.fixture
def user():
    return {
        'name': 'Ali Rida Awad',
        'email': 'ali.awad@example.com',
        'phone': '70123456',
        'address': 'Beirut',
        'country': 'Lebanon',
    }


@pytest.fixture
def saved_user(database, user):
    return db.insert_user(user)


@pytest.fixture
def client(database):
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def read_rows(database):
    """Verify persisted values independently of the functions under test."""
    with sqlite3.connect(database) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute('SELECT * FROM users ORDER BY user_id')]


def test_database_created_with_initial_users_on_first_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    database = tmp_path / 'database.db'
    assert not database.exists()
    # Exercise the actual app startup, replacing only the blocking web server.
    monkeypatch.setattr('flask.Flask.run', lambda self: None)
    runpy.run_path(str(Path(__file__).with_name('app.py')), run_name='__main__')
    assert database.is_file()
    assert read_rows(database) == [{
        'user_id': 1, 'name': 'John Doe', 'email': 'jondoe@gamil.com',
        'phone': '067765434567', 'address': 'John Doe Street, Innsbruck',
        'country': 'Austria',
    }]


def test_second_start_preserves_users_without_duplicates(database, saved_user):
    before = read_rows(database)
    db.initialize_database()
    assert read_rows(database) == before


def test_insert_user(database, user):
    result = db.insert_user(user)
    assert isinstance(result['user_id'], int)
    assert result == dict(user, user_id=2)
    assert read_rows(database)[-1] == result


def test_get_users(database, saved_user):
    assert db.get_users() == read_rows(database)
    assert len(db.get_users()) == 2


def test_get_user_by_id(saved_user):
    assert db.get_user_by_id(saved_user['user_id']) == saved_user


def test_get_user_by_id_missing(database):
    assert db.get_user_by_id(99999) == {}


def test_update_user(database, saved_user):
    updated = dict(saved_user, name='Updated User', email='updated@example.com',
                   phone='03123456', address='Tripoli', country='Lebanon')
    assert db.update_user(updated) == updated
    assert read_rows(database)[-1] == updated
    assert len(read_rows(database)) == 2


def test_delete_user(database, saved_user):
    assert db.delete_user(saved_user['user_id']) == {'status': 'User deleted successfully'}
    assert [row['user_id'] for row in read_rows(database)] == [1]


def test_api_get_users(client, database, saved_user):
    response = client.get('/api/users')
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == read_rows(database)


def test_api_get_user(client, saved_user):
    response = client.get(f"/api/users/{saved_user['user_id']}")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == saved_user


def test_api_add_user(client, database, user):
    response = client.post('/api/users/add', json=user)
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == dict(user, user_id=2)
    assert read_rows(database)[-1] == response.get_json()


def test_api_update_user(client, database, saved_user):
    updated = dict(saved_user, name='New Name', email='new@example.com',
                   phone='76123456', address='Sidon', country='Lebanon')
    response = client.put('/api/users/update', json=updated)
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == updated
    assert read_rows(database)[-1] == updated
    assert len(read_rows(database)) == 2


def test_api_delete_user(client, database, saved_user):
    response = client.delete(f"/api/users/delete/{saved_user['user_id']}")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {'status': 'User deleted successfully'}
    assert [row['user_id'] for row in read_rows(database)] == [1]
