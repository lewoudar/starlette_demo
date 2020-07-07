import dateutil.parser
import pytest

from .helpers import assert_in_dict
from ..utils import Operation, Model


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
    response = client.get(client.app.url_path_for('user_list'))
    assert 200 == response.status_code
    data = [
        {
            'first_name': 'Kevin',
            'last_name': 'Tewouda',
            'pseudo': 'lewoudar',
            'email': 'kevin@gmail.com',
            'created_at': '2020-06-07T16:00:00',
            'id': 1
        },
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'pseudo': 'admin',
            'email': 'johnd@gmail.com',
            'created_at': '2020-06-07T16:00:00',
            'id': 2
        }
    ]
    assert data == response.json()


def create_user(client, data):
    return client.post(client.app.url_path_for('user_list'), json=data)


class TestPostUser:
    def test_should_return_400_error_code_when_payload_is_incorrect(self, client):
        data = {
            'email': 'hell',
            'first_name': 'b',
            'last_name': 'bar',
            'password': 'hello'
        }
        response = create_user(client, data)
        assert 400 == response.status_code
        assert response.json() == {
            'detail': {
                'errors': {
                    'email': ['Not a valid email address.'],
                    'first_name': ['Length must be between 2 and 100.'],
                    'pseudo': ['Missing data for required field.'],
                },
                'input': data
            }
        }

    def test_should_correctly_create_user(self, client):
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
            dateutil.parser.parse(result['created_at'])
        except (KeyError, ValueError):
            pytest.fail('fail to retrieve create_at information')

    def test_websocket_feedback_is_sent(self, client, user_data):
        with client.websocket_connect('/feed') as websocket:
            response = create_user(client, user_data)
            assert websocket.receive_json() == {
                'operation': Operation.CREATE.name,
                'model': Model.USERS.name.lower(),
                'payload': {
                    'id': response.json()['id'],
                    'pseudo': user_data['pseudo']
                }
            }


def test_get_user(client):
    response = client.get(client.app.url_path_for('user_detail', id=1))
    assert 200 == response.status_code
    data = {
        'first_name': 'Kevin',
        'last_name': 'Tewouda',
        'pseudo': 'lewoudar',
        'email': 'kevin@gmail.com',
        'created_at': '2020-06-07T16:00:00',
        'id': 1
    }
    assert data == response.json()


class TestPatchUser:

    def test_should_return_403_error_when_user_is_not_authenticated(self, client):
        response = client.patch(client.app.url_path_for('user_detail', id=1))
        assert 403 == response.status_code

    def test_should_return_403_error_when_user_does_not_have_ownership(self, client, user_data):
        create_user(client, user_data)
        changed = {'first_name': 'JA rule'}
        response = client.patch(client.app.url_path_for('user_detail', id=1), json=changed, auth=('elliot', 'missy'))
        assert 403 == response.status_code
        assert {'detail': 'user elliot does not have rights to edit this resource'} == response.json()

    @pytest.mark.parametrize('auth', [('foo', 'missy'), ('elliot', 'foo')])
    def test_should_return_401_error_when_user_is_not_recognized(self, client, auth, user_data):
        create_user(client, user_data)
        changed = {'first_name': 'JA rule'}
        response = client.patch(client.app.url_path_for('user_detail', id=1), json=changed, auth=auth)
        assert 401 == response.status_code
        assert {'detail': 'pseudo or password incorrect'} == response.json()

    def test_should_return_400_error_when_payload_is_empty(self, client):
        data = {}
        response = client.patch(client.app.url_path_for('user_detail', id=1), json=data, auth=('lewoudar', 'bar'))
        assert 400 == response.status_code
        assert response.json() == {
            'detail': {
                'errors': {'schema': ['payload must not be empty']},
                'input': data
            }
        }

    def test_should_return_400_error_when_payload_is_incorrect(self, client):
        data = {'email': 'hell@fear'}
        response = client.patch(client.app.url_path_for('user_detail', id=1), json=data, auth=('lewoudar', 'bar'))
        assert 400 == response.status_code
        assert response.json() == {
            'detail': {
                'errors': {'email': ['Not a valid email address.']},
                'input': data
            }
        }

    @pytest.mark.parametrize('auth', [
        ('elliot', 'missy'),  # owner
        ('admin', 'admin')  # admin
    ])
    def test_should_change_correctly_user_information(self, client, user_data, auth):
        response = create_user(client, user_data)
        user_id = response.json()['id']
        changed = {'first_name': 'JA rule'}
        response = client.patch(client.app.url_path_for('user_detail', id=user_id), json=changed, auth=auth)
        assert 200 == response.status_code
        response_data = response.json()
        assert response_data['first_name'] == 'JA rule'
        assert response_data['id'] == user_id
        for item in ['last_name', 'pseudo', 'email']:
            assert response_data[item] == user_data[item]

    def test_websocket_feedback_is_sent(self, client):
        with client.websocket_connect('/feed') as websocket:
            changed = {'email': 'lewoudar@hello.com'}
            auth = ('lewoudar', 'bar')
            client.patch(client.app.url_path_for('user_detail', id=1), json=changed, auth=auth)
            assert websocket.receive_json() == {
                'operation': Operation.UPDATE.name,
                'model': Model.USERS.name.lower(),
                'payload': {
                    'id': 1,
                    'pseudo': 'lewoudar'
                }
            }


class TestDeleteUser:

    def test_should_return_403_error_when_user_is_not_authenticated(self, client):
        response = client.delete(client.app.url_path_for('user_detail', id=1))
        assert 403 == response.status_code

    def test_should_return_403_error_when_user_does_not_have_ownership(self, client, user_data):
        create_user(client, user_data)
        response = client.delete(client.app.url_path_for('user_detail', id=1), auth=('elliot', 'missy'))
        assert 403 == response.status_code
        assert {'detail': 'user elliot does not have rights to edit this resource'} == response.json()

    @pytest.mark.parametrize('auth', [('foo', 'missy'), ('elliot', 'foo')])
    def test_should_return_401_error_when_user_is_not_recognized(self, client, user_data, auth):
        response = client.delete(client.app.url_path_for('user_detail', id=1), auth=auth)
        assert 401 == response.status_code
        assert {'detail': 'pseudo or password incorrect'} == response.json()

    @pytest.mark.parametrize('auth', [
        ('lewoudar', 'bar'),  # owner
        ('admin', 'admin')  # admin
    ])
    def test_should_delete_user_when_user_in_action_have_appropriate_rights(self, client, auth):
        response = client.delete(client.app.url_path_for('user_detail', id=1), auth=auth)
        assert 204 == response.status_code
        response = client.get(client.app.url_path_for('user_detail', id=1))
        assert 404 == response.status_code

    def test_websocket_feedback_is_sent(self, client):
        with client.websocket_connect('/feed') as websocket:
            client.delete(client.app.url_path_for('user_detail', id=1), auth=('lewoudar', 'bar'))
            assert websocket.receive_json() == {
                'operation': Operation.DELETE.name,
                'model': Model.USERS.name.lower(),
                'payload': {
                    'id': 1,
                    'pseudo': 'lewoudar'
                }
            }
