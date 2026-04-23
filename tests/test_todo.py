from http import HTTPStatus

import factory.fuzzy
import pytest
from sqlalchemy import select

from projeto1.models import Todo, TodoState, User

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


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
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
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def read_todos_with_all_camps(
    session, token, user, client, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['todos'] == {
        'id': todo.id,
        'title': todo.title,
        'state': todo.state,
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
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
        '/todos/100', headers={'Authorization': f'Bearer {token}'}
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


@pytest.mark.asyncio
async def test_create_todo_error(session, user: User):  # copiado
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='test',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError):
        await session.scalar(select(Todo))


def test_list_todos_filter_min_length_exercicio_06(client, token):
    tiny_string = 'a'
    response = client.get(
        f'/todos/?title={tiny_string}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_todos_filter_max_length_exercicio_06(client, token):
    large_string = 'a' * 22
    response = client.get(
        f'/todos/?title={large_string}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
