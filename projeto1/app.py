from http import HTTPStatus

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException
from projeto1.database import get_session
from projeto1.models import User
from projeto1.schemas import Mensagem, Token, UserList, UserPublic, UserSchema
from projeto1.security import (
    create_access_token,
    get_current_user,
    get_password,
    verify_password,
)

app = FastAPI(title='Minha API!')

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Mensagem)
def read_root():
    return {'mensagem': 'Olá mundo!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if user.username == db_user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exist.',
            )
        elif user.email == db_user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email already exist.'
            )
    hashed_password = get_password(user.password)
    db_user = User(
        username=user.username, email=user.email, password=hashed_password
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    """user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)"""
    return db_user


@app.get('/users/', response_model=UserList)
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.put('/user/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions.'
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password(user.password)

        session.commit()
        session.refresh(current_user)
        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists.',
        )


@app.delete('/users/{user_id}', response_model=Mensagem)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Could enough permissions.',
        )

    session.delete(current_user)
    session.commit()

    return {'mensagem': 'User eliminado.'}


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found.'
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password.',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
