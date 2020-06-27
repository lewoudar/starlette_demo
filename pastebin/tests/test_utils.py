import pytest

from pastebin.utils import get_like_string


@pytest.mark.parametrize(('given', 'expected'), [
    ('python', 'python'),
    ('p*thon', 'p%thon'),
    ('p?thon', 'p_thon'),
    ('p?th*', 'p_th%')
])
def test_get_like_string(given, expected):
    """Tests function get_like_string"""
    assert expected == get_like_string(given)
