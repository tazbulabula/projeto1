from http import HTTPStatus

import factory.fuzzy
import pytest

from projeto1.models import Todo, TodoState

"""
    Se usares pytest-asyncio >= 0.21,
    podes configurar no pytest.ini ou pyproject.toml:
    pytest.ini
    [pytest]
    asyncio_mode = auto
    Assim, o pytest detecta
    automaticamente quando um teste é async def,
    e não precisas colocar @pytest.mark.asyncio em cada função.
"""


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token):
    response = client.post(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Novo teste todo',
            'state': 'draft',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Novo teste todo',
        'state': 'draft',
    }


@pytest.mark.asyncio
async def test_read_todos(session, client, user, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_todo_should_return_with_offset_and_limit(
    session, client, user, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_todo_return_with_filter_title(session, client, user, token):
    expected_todo = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='Todo test 1')
    )

    await session.commit()

    response = client.get(
        '/todos/?title=Todo test 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todo


@pytest.mark.asyncio
async def test_todo_return_with_filter_description(
    session, client, user, token
):
    expected_todo = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description='Todo test 1')
    )

    await session.commit()

    response = client.get(
        '/todos/?description=Todo test 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todo


@pytest.mark.asyncio
async def test_todo_return_with_filter_state(session, client, user, token):
    expected_todo = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft)
    )

    await session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todo


@pytest.mark.asyncio
async def test_todo_return_with_all_filter(session, client, user, token):
    expected_todo = 5

    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Todo teste',
            description='Todo teste 1',
            state=TodoState.todo,
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other test',
            description='Other teste 1',
            state=TodoState.done,
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?title=Todo teste&description=Todo teste 1&state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todo


@pytest.mark.asyncio
async def test_todo_update(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test 1',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'test 1'


def test_todo_update_with_error(client, user, token):
    response = client.patch(
        '/todos/100',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'test 1'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_todo_delete_with_error(client, user, token):
    response = client.delete(
        '/todos/100',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_delete_todo(client, user, token, session):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'mensagem': 'Task deleted.'}
