from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):

    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'mensagem': 'Olá mundo!'}  # Assert
