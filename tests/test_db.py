from dataclasses import asdict

import pytest
from sqlalchemy import select

from projeto1.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='Taz', password='1234', email='taz@gmail.com')
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'Taz'))

    assert asdict(user) == {
        'id': 1,
        'username': 'Taz',
        'email': 'taz@gmail.com',
        'password': '1234',
        'created_at': time,
        'updated_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo(session, user):
    todo = Todo(
        title='Dormir',
        description='Dormir mais cedo.',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == {
        'id': 1,
        'title': 'Dormir',
        'description': 'Dormir mais cedo.',
        'state': 'draft',
        'user_id': 1,
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user):
    todo = Todo(
        title='Dormir',
        description='Dormir mais cedo.',
        state='draft',
        user_id=user.id,
    )
    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(user.id == User.id))

    assert user.todos == [todo]
