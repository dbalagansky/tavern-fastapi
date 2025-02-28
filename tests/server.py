import datetime
from contextlib import asynccontextmanager
from typing import Any, Dict

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Session, SQLModel, create_engine, select

USER = "test-user"
PASSWORD = "correct-password"
SECRET = "CGQgaG7GYvTcpaQZqosLy4"
SERVERNAME = "testserver"


class Number(SQLModel, table=True):
    name: str = Field(primary_key=True)
    number: int


class User(BaseModel):
    name: str
    password: str


engine = create_engine(
    "sqlite:///:memory:?cache=shared",
    echo=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def require_jwt():
    """Makes sure a jwt is in the request before accepting it"""

    def check_jwt(request: Request):
        token = request.headers.get("Authorization")

        if not token:
            return HTTPException(status_code=401, detail="No token")

        token_type, token = token.split(" ")

        if token_type.lower() != "bearer":
            return HTTPException(status_code=401, detail="Wrong token type")

        try:
            jwt.decode(token, SECRET, audience=SERVERNAME, algorithms=["HS256"])
        except Exception:
            return HTTPException(status_code=401, detail="Invalid token")

    return check_jwt


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.state_variable = 42

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {"message": "I'm OK"}


@app.get("/state")
def state(request: Request):
    return {"state_var": request.app.state.state_variable}


@app.post("/login")
def login(user: User):
    if user.name != USER or user.password != PASSWORD:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/password",
        )

    payload = {
        "sub": user.name,
        "aud": SERVERNAME,
        "exp": datetime.datetime.now() + datetime.timedelta(hours=1),
    }

    token = jwt.encode(payload, SECRET, algorithm="HS256")

    return {"token": token}


@app.post("/numbers")
def add_number(
    number: Number,
    session: Session = Depends(get_session),
    _: str = Depends(require_jwt),
):
    if number.number is None:
        return HTTPException(status_code=400, detail="missing key")

    session.add(number)
    session.commit()
    session.refresh(number)

    return Response(status_code=status.HTTP_201_CREATED, media_type="application/json")


@app.get("/numbers")
def get_number(
    name: str,
    session: Session = Depends(get_session),
    _: str = Depends(require_jwt),
):
    n = session.get(Number, name)

    if not n:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown number"
        )

    return {"number": n.number}


@app.post("/double")
def double_number(
    number: Number,
    session: Session = Depends(get_session),
    _: str = Depends(require_jwt),
):
    n = session.get(Number, number.name)

    if not n:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown number"
        )

    n.number *= 2

    session.add(n)
    session.commit()
    session.refresh(n)

    d = session.get(Number, number.name)

    return {"number": d.number}


@app.post("/reset")
def reset(session: Session = Depends(get_session)):
    for number in session.exec(select(Number)).all():
        session.delete(number)

    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
