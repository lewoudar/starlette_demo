from pastebin import app


def test_get_users(client):
    response = client.get(app.url_path_for('user_list'))
    assert 200 == response.status_code
    data = {
        'first_name': 'Kevin',
        'last_name': 'Tewouda',
        'pseudo': 'lewoudar',
        'email': 'foo@gmail.com',
        'id': 1
    }
    assert [data] == response.json()
