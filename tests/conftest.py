from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from projeto1.app import app
from projeto1.database import get_session
from projeto1.models import User, table_registry
from projeto1.security import get_password


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    """create_engine('sqlite:///:memory:'):
        cria um mecanismo de banco de dados SQLite
        em memória usando SQLAlchemy. Este mecanismo
        será usado para criar uma sessão de banco de
        dados para nossos testes."""

    table_registry.metadata.create_all(engine)
    """table_registry.metadata.create_all(engine):
    cria todas as tabelas no banco de dados de teste
    antes de cada teste que usa a fixture session."""

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()  # fecha a conexão com o banco de dados em memória


@contextmanager
def _mock_deb_time(*, model, time=datetime(2025, 1, 1)):
    def fak_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fak_time_hook)
    yield time
    event.remove(model, 'before_insert', fak_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_deb_time


@pytest.fixture
def user(session):
    password = 'testtest'
    user = User(
        username='test',
        email='test@gmail.com',
        password=get_password(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']
