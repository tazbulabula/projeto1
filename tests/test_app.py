from http import HTTPStatus

from projeto1.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):

    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'mensagem': 'Olá mundo!'}  # Assert


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'steinn',
            'email': 'steinn@gmail.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'steinn',
        'email': 'steinn@gmail.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}
    """assert response.json() == {
        'users': [
            {
                'username': 'steinn',
                'email': 'steinn@gmail.com',
                'id': 1,
            }
        ]
    }"""


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Charles',
            'email': 'charles@gmail.com',
            'password': 'secret',
            'id': user.id,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Charles',
        'email': 'charles@gmail.com',
        'id': user.id,
    }


def test_update_integrity_error(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'Agostinho',
            'email': 'agostinho@gmail.com',
            'password': 'secret',
        },
    )

    response_update = client.put(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Agostinho',
            'email': 'agostinho@gmail.com',
            'password': '123',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists.'
    }


"""def test_update_user_not_found(client, token):
    response = client.put(
        f'/user/{2}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Agostinho',
            'email': 'agostinho@gmail.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found.'}
"""


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'mensagem': 'User eliminado.'}


"""def test_delete_user_not_found(client, user, token):
    response = client.delete(
        f'/users/{2}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found.'}"""


def test_get_token(client, user):

    response_token = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response_token.json()

    assert response_token.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
