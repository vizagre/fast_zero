from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'A API está funcionando!'}


def test_create_user_deve_criar_usuario_e_retornar_ok(client):
    user_data = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'alice',
                'email': 'alice@example.com',
            }
        ]
    }


def test_read_user(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_user_inexistente(client):
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_update_user(client):
    user_data = {
        'username': 'alice_updated',
        'email': 'alice_updated@example.com',
        'password': 'new_secret',
    }

    response = client.put('/users/1', json=user_data)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice_updated',
        'email': 'alice_updated@example.com',
    }


def test_update_user_inexistente(client):
    user_data = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'secret',
    }

    response = client.put('/users/999', json=user_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice_updated',
        'email': 'alice_updated@example.com',
    }


def test_delete_user_inexistente(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}
