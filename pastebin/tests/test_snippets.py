import dateutil.parser
import pytest

from pastebin.snippets.models import LANGUAGES, STYLES
from .helpers import assert_in_dict
from ..utils import Operation, Model


@pytest.fixture()
def snippet_data():
    return {
        'title': 'just a snippet',
        'code': "print('hello')",
        'language': 'python',
        'style': 'default'
    }


class TestGetLanguages:

    def test_should_return_languages_without_filter(self, client):
        response = client.get(client.app.url_path_for('snippet_languages'))
        assert response.status_code == 200
        assert response.json() == LANGUAGES

    @pytest.mark.parametrize(('name', 'expected_result'), [
        ('p?thon', ['python']),
        ('pyth*', ['python', 'python2'])
    ])
    def test_should_return_languages_with_filter(self, client, name, expected_result):
        response = client.get(client.app.url_path_for('snippet_languages'), params={'name': name})
        assert response.status_code == 200
        assert response.json() == expected_result


class TestGetStyles:

    def test_should_return_styles_without_filter(self, client):
        response = client.get(client.app.url_path_for('snippet_styles'))
        assert response.status_code == 200
        assert response.json() == STYLES

    @pytest.mark.parametrize(('name', 'expected_result'), [
        ('*i', ['manni', 'monokai']),
        ('v?*', ['vim', 'vs'])
    ])
    def test_should_return_styles_with_filter(self, client, name, expected_result):
        response = client.get(client.app.url_path_for('snippet_styles'), params={'name': name})
        assert response.status_code == 200
        assert response.json() == expected_result


def test_get_snippets(client):
    response = client.get(client.app.url_path_for('snippet_list'))
    assert response.status_code == 200
    assert response.json() == [
        {
            'id': 1,
            'title': 'first snippet',
            'code': 'print("hello world!")',
            'linenos': True,
            'language': 'python',
            'style': 'friendly',
            'highlight': f'{client.base_url}{client.app.url_path_for("snippet_highlight", id=1)}',
            'user': f'{client.base_url}{client.app.url_path_for("user_detail", id=1)}',
            'created_at': '2020-06-28T12:35:00'
        }
    ]


def create_snippet(client, data, linenos=True, auth=('lewoudar', 'bar')):
    if linenos:
        data['linenos'] = True
    return client.post(client.app.url_path_for('snippet_list'), json=data, auth=auth)


class TestPostSnippet:

    def test_should_return_403_error_when_user_is_not_authenticated(self, client):
        response = client.post(client.app.url_path_for('snippet_list'))
        assert response.status_code == 403

    def test_should_return_401_error_when_user_is_not_recognized(self, client):
        response = client.post(client.app.url_path_for('snippet_list'), auth=('foo', 'bar'))
        assert response.status_code == 401

    def test_should_return_400_error_when_payload_is_incorrect(self, client):
        data = {
            'title': 'title',
            'style': 'foo',
            'language': 'python',
        }
        response = client.post(client.app.url_path_for('snippet_list'), json=data, auth=('lewoudar', 'bar'))
        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'input': data,
                'errors': {
                    'style': [f'Must be one of: {", ".join(STYLES)}.'],
                    'code': ['Missing data for required field.']
                }
            }
        }

    @pytest.mark.parametrize('linenos', [True, False])
    def test_should_create_snippet(self, client, snippet_data, linenos):
        response = create_snippet(client, snippet_data, linenos=linenos)
        assert response.status_code == 200
        result = response.json()
        assert_in_dict(snippet_data, result)
        assert result['id'] == 2
        assert result['linenos'] == linenos
        try:
            dateutil.parser.parse(result['created_at'])
        except (KeyError, ValueError):
            pytest.fail('fail to retrieve create_at information')

    def test_websocket_feedback_is_sent(self, client, snippet_data):
        with client.websocket_connect('/feed') as websocket:
            response = create_snippet(client, snippet_data)
            assert websocket.receive_json() == {
                'operation': Operation.CREATE.name,
                'model': Model.SNIPPETS.name.lower(),
                'payload': {
                    'id': response.json()['id'],
                    'owner': 'lewoudar',
                    'title': snippet_data['title']
                }
            }


def test_get_snippet(client):
    response = client.get(client.app.url_path_for('snippet_detail', id=1))
    assert response.status_code == 200
    assert response.json() == {
        'id': 1,
        'title': 'first snippet',
        'code': 'print("hello world!")',
        'linenos': True,
        'language': 'python',
        'style': 'friendly',
        'highlight': f'{client.base_url}{client.app.url_path_for("snippet_highlight", id=1)}',
        'user': f'{client.base_url}{client.app.url_path_for("user_detail", id=1)}',
        'created_at': '2020-06-28T12:35:00'
    }


class TestPatchSnippet:

    def test_should_return_403_error_when_user_is_not_authenticated(self, client):
        response = client.patch(client.app.url_path_for('snippet_detail', id=1))
        assert 403 == response.status_code

    def test_should_return_403_error_when_user_does_not_have_ownership(self, client, snippet_data):
        response = create_snippet(client, snippet_data, auth=('admin', 'admin'))
        snippet_id = response.json()['id']
        data = {'linenos': True}
        auth = ('lewoudar', 'bar')
        response = client.patch(client.app.url_path_for('snippet_detail', id=snippet_id), json=data, auth=auth)

        assert response.status_code == 403

    def test_should_return_401_error_when_user_is_not_recognized(self, client):
        response = client.patch(client.app.url_path_for('snippet_detail', id=1), auth=('foo', 'bar'))
        assert response.status_code == 401

    def test_should_return_400_error_when_payload_is_incorrect(self, client):
        data = {
            'linenos': 2,
            'title': 'title',
            'language': 'python',
            'code': 'hello'
        }
        response = client.patch(client.app.url_path_for('snippet_detail', id=1), json=data, auth=('lewoudar', 'bar'))
        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'input': data,
                'errors': {
                    'linenos': ['Not a valid boolean.']
                }
            }
        }

    @pytest.mark.parametrize('auth', [
        ('lewoudar', 'bar'),  # normal user
        ('admin', 'admin')  # admin user
    ])
    def test_should_return_correct_updated_data(self, client, auth):
        data = {'style': 'monokai'}
        response = client.patch(client.app.url_path_for('snippet_detail', id=1), json=data, auth=auth)
        assert response.status_code == 200
        assert response.json() == {
            'id': 1,
            'title': 'first snippet',
            'code': 'print("hello world!")',
            'linenos': True,
            'language': 'python',
            'style': 'monokai',
            'highlight': f'{client.base_url}{client.app.url_path_for("snippet_highlight", id=1)}',
            'user': f'{client.base_url}{client.app.url_path_for("user_detail", id=1)}',
            'created_at': '2020-06-28T12:35:00'
        }

    def test_websocket_feedback_is_sent(self, client):
        with client.websocket_connect('/feed') as websocket:
            data = {'style': 'default'}
            auth = ('lewoudar', 'bar')
            client.patch(client.app.url_path_for('snippet_detail', id=1), json=data, auth=auth)
            assert websocket.receive_json() == {
                'operation': Operation.UPDATE.name,
                'model': Model.SNIPPETS.name.lower(),
                'payload': {
                    'id': 1,
                    'owner': 'lewoudar',
                    'title': 'first snippet'
                }
            }


class TestDeleteSnippet:

    def test_should_return_403_error_when_user_is_not_authenticated(self, client):
        response = client.delete(client.app.url_path_for('snippet_detail', id=1))
        assert response.status_code == 403

    def test_should_return_403_error_when_user_does_not_have_ownership(self, client, snippet_data):
        response = create_snippet(client, snippet_data, auth=('admin', 'admin'))
        snippet_id = response.json()['id']
        response = client.delete(client.app.url_path_for('snippet_detail', id=snippet_id), auth=('lewoudar', 'bar'))

        assert response.status_code == 403

    def test_should_return_401_error_when_user_is_not_recognized(self, client):
        response = client.delete(client.app.url_path_for('snippet_detail', id=1), auth=('foo', 'bar'))
        assert response.status_code == 401

    @pytest.mark.parametrize('auth', [
        ('lewoudar', 'bar'),  # normal user
        ('admin', 'admin')  # admin user
    ])
    def test_should_correctly_delete_snippet(self, client, auth):
        response = client.delete(client.app.url_path_for('snippet_detail', id=1), auth=auth)
        assert response.status_code == 204
        response = client.get(client.app.url_path_for('snippet_detail', id=1))
        assert response.status_code == 404

    def test_websocket_feedback_is_sent(self, client):
        with client.websocket_connect('/feed') as websocket:
            client.delete(client.app.url_path_for('snippet_detail', id=1), auth=('lewoudar', 'bar'))
            assert websocket.receive_json() == {
                'operation': Operation.DELETE.name,
                'model': Model.SNIPPETS.name.lower(),
                'payload': {
                    'id': 1,
                    'owner': 'lewoudar',
                    'title': 'first snippet'
                }
            }


@pytest.mark.skip('seems there is an issue with the test client when using templating..')
def test_get_highlighted(client):
    response = client.get(client.app.url_path_for('snippet_highlight', id=1))
    assert response.status_code == 200
    assert response.template.name == 'highlight.jinja2'
    assert 'request' in response.context
    assert response.context['title'] == 'first snippet'
    assert '<h2>first snippet</h2>' in response.text
    assert 'hello world' in response.text
