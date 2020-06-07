from datetime import datetime

import pytest

from pastebin import app
from .utils import assert_in_dict


def test_get_users(client):
    response = client.get(app.url_path_for('user_list'))
    assert 200 == response.status_code
    data = {
        'first_name': 'Kevin',
        'last_name': 'Tewouda',
        'pseudo': 'lewoudar',
        'email': 'foo@gmail.com',
        'created_at': '2020-06-07 16:00:00',
        'id': 1
    }
    assert [data] == response.json()


def create_user(client, data):
    return client.post(app.url_path_for('user_list'), json=data)


def test_post_user(client):
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'pseudo': 'zoro',
        'email': 'john.doe@gmail.com',
        'password': 'pass'
    }
    response = create_user(client, data)
    assert 201 == response.status_code
    data.pop('password')
    result = response.json()
    assert_in_dict(data, result)
    try:
        datetime.strptime(result['created_at'], '%Y-%m-%d %H:%M:%S')
    except (KeyError, ValueError):
        pytest.fail('fail to retrieve create_at information')


def test_get_user(client):
    response = client.get(app.url_path_for('user_detail', id=1))
    assert 200 == response.status_code
    data = {
        'first_name': 'Kevin',
        'last_name': 'Tewouda',
        'pseudo': 'lewoudar',
        'email': 'foo@gmail.com',
        'created_at': '2020-06-07 16:00:00',
        'id': 1
    }
    assert data == response.json()


def test_put_user(client):
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'pseudo': 'zoro',
        'email': 'john.doe@gmail.com',
        'password': 'pass'
    }
    response = create_user(client, data)
    data.pop('password')
    data['pseudo'] = 'johnd'
    response = client.put(app.url_path_for('user_detail', id=response.json()['id']), json=data)
    assert 200 == response.status_code
    assert_in_dict(data, response.json())


def test_delete_user(client):
    response = client.delete(app.url_path_for('user_detail', id=1))
    assert 204 == response.status_code
    response = client.get(app.url_path_for('user_detail', id=1))
    assert 404 == response.status_code
