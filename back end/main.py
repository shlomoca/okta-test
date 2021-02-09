from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import httpx
from starlette.config import Config
from typing import List
from pydantic import BaseModel
from okta_jwt.jwt import validate_token as validate_locally
from fastapi.middleware.cors import CORSMiddleware

config = Config('.env.example')

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:8000/api/messages",
    "http://localhost:8080/api/messages",
    "http://127.0.0.1:8000/api/messages",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def retrieve_token(authorization, issuer, scope='items'):
    headers = {
        'accept': 'application/json',
        'authorization': authorization,
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'scope': scope,
    }
    url = issuer + '/v1/token'

    response = httpx.post(url, headers=headers, data=data)

    if response.status_code == httpx.codes.OK:
        return response.json()
    else:
        raise HTTPException(status_code=400, detail=response.text)


# # Open, Hello World route
@app.get('/')
def read_root():
    return {'Hello': 'World'}


# Get auth token
@app.post('/token')
def login(request: Request):
    return retrieve_token(
        request.headers['authorization'],
        config('OKTA_ISSUER'),
        'items'
    )


def validate_remotely(token, issuer, clientId, clientSecret):
    headers = {
        'accept': 'application/json',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
    }
    data = {
        'client_id': clientId,
        'client_secret': clientSecret,
        'token': token,
    }
    url = issuer + '/v1/introspect'

    response = httpx.post(url, headers=headers, data=data)

    return response.status_code == httpx.codes.OK and response.json()['active']


def validate(token: str = Depends(oauth2_scheme)):
    # Remote validation
    # res = validate_remotely(
    #     token,
    #     config('OKTA_ISSUER'),
    #     config('OKTA_CLIENT_ID'),
    #     config('OKTA_CLIENT_SECRET')
    # )

    # Local validation
    return True
    try:
        res = validate_locally(
            token,
            config('OKTA_ISSUER'),
            config('OKTA_AUDIENCE'),
            config('OKTA_CLIENT_ID')
        )
        return bool(res)
    except Exception:
        raise HTTPException(status_code=403)


class Item(BaseModel):
    id: int
    name: str


# Protected, get items route
@app.get('/items', response_model=List[Item])
def read_items(valid: bool = Depends(validate)):
    return [
        Item.parse_obj({'id': 1, 'name': 'red ball'}),
        Item.parse_obj({'id': 2, 'name': 'blue square'}),
        Item.parse_obj({'id': 3, 'name': 'purple ellipse'}),
    ]


# Protected, get items route
@app.get('/api/messages', response_model=List[Item])
async def read_messages(valid: bool = Depends(validate)):
    return [
        Item.parse_obj({'id': 1, 'name': 'red ball'}),
        Item.parse_obj({'id': 2, 'name': 'blue square'}),
        Item.parse_obj({'id': 3, 'name': 'purple ellipse'}),
    ]
