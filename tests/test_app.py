from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):

    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'mensagem': 'Olá mundo!'}  # Assert


def test_creat_user(client):
    response = client.post(
        '/users/',
        json={'username': 'taz', 'email': 'taz@gmail.com', 'password': '123'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'taz',
        'email': 'taz@gmail.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'taz',
                'email': 'taz@gmail.com',
                'id': 1,
            }
        ]
    }


def test_update_user(client):
    response = client.put(
        '/user/1',
        json={
            'username': 'Charles',
            'email': 'charles@gmail.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Charles',
        'email': 'charles@gmail.com',
        'id': 1,
    }


def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'mensagem': 'User eliminado.'}
