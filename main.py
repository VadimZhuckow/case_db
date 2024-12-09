import asyncio
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = "postgresql://new_user:0000@db/new_database"

class User(BaseModel):
    username: str
    email: str

async def connect_db():
    for _ in range(5):  # Попытаемся подключиться 5 раз
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except psycopg2.OperationalError:
            print("Не удалось подключиться к базе данных. Повторная попытка через 5 секунд...")
            await asyncio.sleep(5)
    raise Exception("Не удалось подключиться к базе данных после 5 попыток")

@app.on_event("startup")
async def startup():
    try:
        conn = await connect_db()
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
    except Exception as e:
        print(f"Error during startup: {e}")
        raise

@app.post("/register", status_code=201)
async def register_user(user: User):
    try:
        conn = await connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            (user.username, user.email)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "User created successfully"}
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users", status_code=200)
async def get_user():
    conn = await connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"users": [dict(zip(["id", "username", "email"], user)) for user in users]}