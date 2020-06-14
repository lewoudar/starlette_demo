from datetime import datetime

import pytest

from pastebin import app
from .utils import assert_in_dict


@pytest.fixture(scope='module')
def user_data():
    return {
        'first_name': 'Missy',
        'last_name': 'Elliot',
        'pseudo': 'elliot',
        'email': 'elliot@gmail.com',
        'password': 'missy'
    }


def test_get_users(client):
    response = client.get(app.url_path_for('user_list'))
    assert 200 == response.status_code
    data = [
        {
            'first_name': 'Kevin',
            'last_name': 'Tewouda',
            'pseudo': 'lewoudar',
            'email': 'kevin@gmail.com',
            'created_at': '2020-06-07 16:00:00',
            'id': 1
        },
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'pseudo': 'admin',
            'email': 'johnd@gmail.com',
            'created_at': '2020-06-07 16:00:00',
            'id': 2
        }
    ]
    assert data == response.json()


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
        'email': 'kevin@gmail.com',
        'created_at': '2020-06-07 16:00:00',
        'id': 1
    }
    assert data == response.json()


class TestPatchUser:

    def test_should_return_403_error_when_user_is_not_authenticated(self, client):
        response = client.patch(app.url_path_for('user_detail', id=1))
        assert 403 == response.status_code

    def test_should_return_403_error_when_user_does_not_have_ownership(self, client, user_data):
        create_user(client, user_data)
        changed = {'first_name': 'JA rule'}
        response = client.patch(app.url_path_for('user_detail', id=1), json=changed, auth=('elliot', 'missy'))
        assert 403 == response.status_code
        assert {'detail': 'user elliot does not have rights to edit this resource'} == response.json()

    @pytest.mark.parametrize('auth', [('foo', 'missy'), ('elliot', 'foo')])
    def test_should_return_401_error_when_user_is_not_recognized(self, client, auth, user_data):
        create_user(client, user_data)
        changed = {'first_name': 'JA rule'}
        response = client.patch(app.url_path_for('user_detail', id=1), json=changed, auth=auth)
        assert 401 == response.status_code
        assert {'detail': 'pseudo or password incorrect'} == response.json()

    @pytest.mark.parametrize('auth', [
        ('elliot', 'missy'),  # owner
        ('admin', 'admin')  # admin
    ])
    def test_should_change_correctly_user_information(self, client, user_data, auth):
        response = create_user(client, user_data)
        user_id = response.json()['id']
        changed = {'first_name': 'JA rule'}
        response = client.patch(app.url_path_for('user_detail', id=user_id), json=changed, auth=auth)
        assert 200 == response.status_code
        response_data = response.json()
        assert response_data['first_name'] == 'JA rule'
        assert response_data['id'] == user_id
        for item in ['last_name', 'pseudo', 'email']:
            assert response_data[item] == user_data[item]


class TestDeleteUser:

    def test_should_return_403_error_when_user_is_not_authenticated(self, client):
        response = client.delete(app.url_path_for('user_detail', id=1))
        assert 403 == response.status_code

    def test_should_return_403_error_when_user_does_not_have_ownership(self, client, user_data):
        create_user(client, user_data)
        response = client.delete(app.url_path_for('user_detail', id=1), auth=('elliot', 'missy'))
        assert 403 == response.status_code
        assert {'detail': 'user elliot does not have rights to edit this resource'} == response.json()

    @pytest.mark.parametrize('auth', [('foo', 'missy'), ('elliot', 'foo')])
    def test_should_return_401_error_when_user_is_not_recognized(self, client, user_data, auth):
        response = client.delete(app.url_path_for('user_detail', id=1), auth=auth)
        assert 401 == response.status_code
        assert {'detail': 'pseudo or password incorrect'} == response.json()

    @pytest.mark.parametrize('auth', [
        ('lewoudar', 'bar'),  # owner
        ('admin', 'admin')  # admin
    ])
    def test_should_delete_user_when_user_in_action_have_appropriate_rights(self, client, auth):
        response = client.delete(app.url_path_for('user_detail', id=1), auth=auth)
        assert 204 == response.status_code
        response = client.get(app.url_path_for('user_detail', id=1))
        assert 404 == response.status_code
