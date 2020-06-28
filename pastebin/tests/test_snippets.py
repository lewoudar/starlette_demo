import dateutil.parser
import pytest

from pastebin.snippets.models import LANGUAGES, STYLES
from .helpers import assert_in_dict


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
            'title': 'first snippet',
            'code': 'print("hello world!")',
            'linenos': True,
            'language': 'python',
            'style': 'friendly',
            'user': f'{client.base_url}{client.app.url_path_for("user_detail", id=1)}',
            'created_at': '2020-06-28T12:35:00'
        }
    ]


def create_snippet(client, data, linenos=True):
    if linenos:
        data['linenos'] = True
    return client.post(client.app.url_path_for('snippet_list'), json=data, auth=('lewoudar', 'bar'))


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
        assert result['linenos'] == linenos
        try:
            dateutil.parser.parse(result['created_at'])
        except (KeyError, ValueError):
            pytest.fail('fail to retrieve create_at information')
