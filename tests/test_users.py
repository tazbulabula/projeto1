from http import HTTPStatus

from projeto1.schemas import UserPublic


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


def test_create_user_with_username_existent(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'password': 'secret',
            'email': 'example@gmail.com',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exist.'}


def test_create_user_with_email_existent(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'username_example',
            'email': user.email,
            'password': 'testet',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exist.'}


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
        f'/users/{user.id}',
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


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'steinn',
            'email': 'steinn@gmail.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'steinn',
        'email': 'steinn@gmail.com',
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


def test_update_user_with_user_wrong(client, other_user, token):

    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions.'}


def test_delete_user_with_user_wrong(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Could enough permissions.'}
