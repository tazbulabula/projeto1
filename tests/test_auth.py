from http import HTTPStatus


def test_get_token(client, user):

    response_token = client.post(
        'auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response_token.json()

    assert response_token.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
