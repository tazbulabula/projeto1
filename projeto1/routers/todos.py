from http import HTTPStatus
from typing import Annotated

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException, Query
from projeto1.database import get_session
from projeto1.models import Todo, User
from projeto1.schemas import (
    FilterTodo,
    Mensagem,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from projeto1.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
async def create_todo(user: CurrentUser, todo: TodoSchema, session: Session):
    todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return jsonable_encoder(todo)


@router.get('/', response_model=TodoList)
async def read_todos(
    user: CurrentUser,
    session: Session,
    filter_todo: Annotated[FilterTodo, Query()],
):

    query = select(Todo).where(Todo.user_id == user.id)

    if filter_todo.title:
        query = query.filter(Todo.title.contains(filter_todo.title))

    if filter_todo.description:
        query = query.filter(
            Todo.description.contains(filter_todo.description)
        )

    if filter_todo.state:
        query = query.filter(Todo.state == filter_todo.state)

    todos = await session.scalars(
        query.offset(filter_todo.offset).limit(filter_todo.limit)
    )

    return {'todos': todos.all()}


@router.patch('/{todo_id}', response_model=TodoPublic)
async def update_todo(
    todo_id: int, user: CurrentUser, session: Session, todo: TodoUpdate
):
    db_todo = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    for (
        key,
        value,
    ) in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', response_model=Mensagem)
async def delete_todo(todo_id: int, user: CurrentUser, session: Session):
    db_todo = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )
    await session.delete(db_todo)

    return {'mensagem': 'Task deleted.'}
