import os
from fastapi import Security, Header, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST

api_key_header = APIKeyHeader(name='x-api-key')

def auth(x_api_key: str = Security(api_key_header)):
    if x_api_key != os.getenv('API_KEY'):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Incorrect API key')


def user_id(x_user_id: str | None = Header(None)):
    if x_user_id is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Missing user id')
    return x_user_id
