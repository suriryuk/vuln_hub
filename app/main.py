from fastapi import FastAPI

import pymysql
from pymysql.err import OperationalError
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Database Connect...')

    try:
        conn = pymysql.connect(host='vuln_db', user='user', password='password', db='vuln', charset='utf8')

        if conn:
            cur = conn.cursor()
        else:
            print('Database Connection Failed..')
            exit(-1)
    except OperationalError:
        print('Can\'t connect to MySQL server')

    yield # yield를 기준으로 위에가 app 실행 때 실행할 명령, 아래가 종료후 실행할 명령

    print('Resource Clear..')
    conn.close()

app = FastAPI(lifespan=lifespan)

@app.get('/')
def root():
    return {'message': 'hello world'}
