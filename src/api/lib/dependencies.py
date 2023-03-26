import os
from fastapi import Depends, Security, Header, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from api.user import UserRepository
from models.user import DBUser
from .exceptions import RepositoryInvalidIdError

api_key_header = APIKeyHeader(name='x-api-key')

def on_auth(x_api_key: str = Security(api_key_header)):
    if x_api_key != os.getenv('API_KEY'):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Incorrect API key')


def on_user_id(x_user_id: str | None = Header(None)):
    if x_user_id is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Missing user id')
    return x_user_id


def on_user(x_user_id: str = Depends(on_user_id)) -> DBUser:
    try:
        user = UserRepository.read(x_user_id)
    except RepositoryInvalidIdError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid user id')
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    return user
