#!../bin/python
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from ssl import cert_time_to_seconds
from fastapi import FastAPI, Form, HTTPException, Response, Cookie, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone
import os

python_path = os.environ.get("PYTHONPATH")
log_file_path = f"{python_path}logs/trading.log"
file_format = "%(asctime)s - %(levelname)s - %(message)s"
stdout_format = "%(levelname)s:     %(message)s"
# Create handlers
file_handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(file_format))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(stdout_format))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

app = FastAPI()
# Secret key to sign JWT tokens
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
# Token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 20
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Sqlite_db(): # pragma: no cover
    def database_create_user_table(self):
        with sqlite3.connect('trading_database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')

    def database_create_user(self, username: str, password: str):
        with sqlite3.connect('trading_database.db') as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    'INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, password))
            except sqlite3.IntegrityError:
                print("Warn: The user alredy exists in the database")

    def database_select_user_by_username(self, username: str) -> tuple | None:
        with sqlite3.connect('trading_database.db') as connection:
            cursor = connection.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,))
            row = cursor.fetchone()
            return row

    def database_create_session_table(self):
        with sqlite3.connect('trading_database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                jwt_token TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id));''')

    def create_session(self, user_id: int, session_token: str):
        with sqlite3.connect('trading_database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('''INSERT INTO sessions
                (user_id, jwt_token)
                VALUES (?, ?)''', (user_id, session_token))

    def get_session_by_jwt(self, session_token: str):
        with sqlite3.connect('trading_database.db') as connection:
            cursor = connection.cursor()
            cursor.execute(
                '''SELECT * FROM sessions WHERE jwt_token = (?)''',
                (session_token,))
            row = cursor.fetchone()
            print(row)


def validate_user(user_record: tuple, username: str, password: str) -> bool:
    if username != user_record[1]:
        return False
    if password != user_record[2]:
        return False
    return True


# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def auth_user(session_token: str = Cookie(None, alias='access_token')):
    credentials_exceptions = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"})
    credentials_expired_exceptions = HTTPException(
        status_code=401,
        detail="Token has expired.",
        headers={"WWW-Authenticate": "Bearer"})
    credentials_audience_exceptions = HTTPException(
        status_code=401,
        detail="Token was provided to a invalid audience.",
        headers={"WWW-Authenticate": "Bearer"})
    credentials_issuer_exceptions = HTTPException(
        status_code=401,
        detail="Token is from a invalid issuer.",
        headers={"WWW-Authenticate": "Bearer"})

    if not session_token:
        logger.info("auth_user: No session token was provided by requester.")
        raise credentials_exceptions
    try:
        payload = jwt.decode(
            session_token,
            SECRET_KEY,
            audience="tradingapi",
            issuer="tradingapi",
            algorithms=[ALGORITHM])
        logger.info("auth_user: The token provided was a valid token")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("auth_user: The session token provided by the requester has expired.")
        raise credentials_expired_exceptions
    except jwt.InvalidAudienceError:
        logger.warning("auth_user: The session token was provided to a invalid audience.")
        raise credentials_audience_exceptions
    except jwt.InvalidIssuerError:
        logger.warning("auth_user: The session token is from a invalid issuer.")
        raise credentials_issuer_exceptions
    except jwt.InvalidTokenError:
        logger.warning("auth_user: The session token provided by the requester is not valid.")
        raise credentials_exceptions


@app.get("/")
def home():
    return "Hello World"


@app.post("/login")
async def login(
        response: Response,
        username: str = Form(),
        password: str = Form()):
    db = Sqlite_db()
    user_record = db.database_select_user_by_username(username)
    if user_record and validate_user(user_record, username, password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        cookie_expires = datetime.utcnow() + access_token_expires
        cookie_expires_utc = cookie_expires.replace(tzinfo=timezone.utc)
        access_token = create_access_token(
            data={
                "sub": username,
                "iss": "tradingapi",
                "aud": "tradingapi"},
            expires_delta=access_token_expires)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True)
        return "User has been logged in"
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/protected-route")
async def protected_route(current_user: dict = Depends(auth_user)):
    return {"message": "This is a protected route", "user": current_user}


if __name__ == "__main__": # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
