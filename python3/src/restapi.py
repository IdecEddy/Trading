from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import jwt

app = FastAPI()

# Secret key to sign and verify the JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 30

user_database = {
    "username": "eddy",
    "password": "123",
}

# OAuth2PasswordBearer for access token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def confirm_database_user(username: str, password: str):
    if (username != user_database['username']
            or password != user_database['password']):
        return False
    return True


def decode_refresh_token(token: str):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_auth_token(token: str, reload_token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        if decode_refresh_token(reload_token):
            token = create_jwt_token(
                {"sub": "123"},
                timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            return token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get('/')
def home():
    return JSONResponse("Hello")


@app.post('/login')
def token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    username = form_data.username
    password = form_data.password

    if not confirm_database_user(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},)

    access_token = create_jwt_token(
        {"sub": username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_jwt_token(
        {"sub": username},
        timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(
        key="JWT-Refresh",
        value=refresh_token,
        httponly=True,
        secure=True
    )

    return {"access_token": access_token}


@app.get("/protected")
def protected_route(
    request: Request,
    auth_token: str = Depends(oauth2_scheme),
):
    reload_token = request.cookies.get("JWT-Refresh")
    if reload_token:
        decode_auth_token(auth_token, reload_token)
        return {"message": "This is a protected route"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
