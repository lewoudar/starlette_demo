import pytest

from pastebin import app
from pastebin.snippets.models import LANGUAGES, STYLES


class TestGetLanguages:

    def test_should_return_languages_without_filter(self, client):
        response = client.get(app.url_path_for('snippet_languages'))
        assert response.status_code == 200
        assert response.json() == LANGUAGES

    @pytest.mark.parametrize(('name', 'expected_result'), [
        ('p?thon', ['python']),
        ('pyth*', ['python', 'python2'])
    ])
    def test_should_return_languages_with_filter(self, client, name, expected_result):
        response = client.get(app.url_path_for('snippet_languages'), params={'name': name})
        assert response.status_code == 200
        assert response.json() == expected_result


class TestGetStyles:

    def test_should_return_styles_without_filter(self, client):
        response = client.get(app.url_path_for('snippet_styles'))
        assert response.status_code == 200
        assert response.json() == STYLES

    @pytest.mark.parametrize(('name', 'expected_result'), [
        ('*i', ['manni', 'monokai']),
        ('v?*', ['vim', 'vs'])
    ])
    def test_should_return_styles_with_filter(self, client, name, expected_result):
        response = client.get(app.url_path_for('snippet_styles'), params={'name': name})
        assert response.status_code == 200
        assert response.json() == expected_result
