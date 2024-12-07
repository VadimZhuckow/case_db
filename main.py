from http.client import HTTPException

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel
import psycopg2
import psycopg2.extras

app = FastAPI()

DATABASE_URL = ""


class User(BaseModel):
    username: str
    email: str


def connect_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.on_event("startup")
def startup():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username varchar(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()


@app.post("/register", status_code=201)
def register_user(user: User):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")


        cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (user.username, user.email))
        conn.commit()
        return {"message": "Пользователь успешно зарегистрирован"}

    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Невалидная почта")
    finally:
        cursor.close()
        conn.close()


@app.get("/users", status_code=200)
def get_user():
    conn = connect_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
    return {"users": [dict(user) for user in users]}

# try:
#     con = psycopg2.connect(DATABASE_URL)
#     print('успех')
# except:
#     print('не успех')
