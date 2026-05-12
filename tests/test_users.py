from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_create_user_deve_criar_usuario_e_retornar_ok(client):
    user_data = {
        'username': 'Teste',
        'email': 'teste@test.com',
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'Teste',
        'email': 'teste@test.com',
    }


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_user(client, user, token):
    response = client.get(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'Teste',
        'email': 'teste@test.com',
    }


def test_read_user_inexistente(client, token):
    response = client.get(
        '/users/999', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_update_user(client, user, token):
    user_data = {
        'username': 'alice_updated',
        'email': 'alice_updated@example.com',
        'password': 'new_secret',
    }

    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
        json=user_data,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice_updated',
        'email': 'alice_updated@example.com',
    }


def test_update_user_inexistente(client, token):
    user_data = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'secret',
    }

    response = client.put(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
        json=user_data,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para atualizar este usuário'
    }


def test_delete_user(client, user, token):
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'Teste',
        'email': 'teste@test.com',
    }


def test_delete_user_inexistente(client, token):
    response = client.delete(
        '/users/999', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_update_integrity_error(client, user, token):
    # Criando um registro para "fausto"
    client.post(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )
    # Alterando o user.username das fixture para fausto
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Usuário com esse nome ou email já existe'
    }


def test_create_user_should_return_409_username_exists_exercicio(
    client, user, token
):
    response = client.post(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Usuário com esse nome já existe'}


def test_create_user_should_return_409_email_exists_exercicio(
    client, user, token
):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Usuário com esse email já existe'}


def test_delete_user_should_return_not_found_exercicio(client):
    response = client.delete('/users/666')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_update_user_should_return_not_found_exercicio(client, token):
    response = client.put(
        '/users/666',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para atualizar este usuário'
    }


def test_get_user_should_return_not_found_exercicio(client, token):
    response = client.get(
        '/users/666', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_get_user_exercicio(client, user, token):
    response = client.get(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }
