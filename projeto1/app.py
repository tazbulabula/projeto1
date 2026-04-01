from http import HTTPStatus

from fastapi import FastAPI
from projeto1.routers import auth, todos, users
from projeto1.schemas import Mensagem

app = FastAPI(title='Minha API!')
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Mensagem)
async def read_root():

    return {'mensagem': 'Olá mundo!'}
