from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import pymysql
from pymysql.err import OperationalError
from contextlib import asynccontextmanager

from db.session import db_engine
from db.base import Base
from routers import auth

def create_table():
    Base.metadata.create_all(bind=db_engine)

def get_application():
    app = FastAPI()
    create_table()
    return app

app = get_application()

app.include_router(auth.router)
app.mount('/assets', StaticFiles(directory='static'))

@app.get('/')
def root():
    return {'message': 'hello world'}
