import requests
import psycopg2
import pytest
from faker import Faker

fake = Faker()


class TestDb:
    API_URL = "http://127.0.0.1:8000/register"
    DATABASE_URL = ""

    def setup_method(self):
        self.test_user = {
            "username": fake.name(),
            "email": fake.email()
        }

    @pytest.mark.user
    def test_create_user(self):
        """
        Функция создает нового пользователя в базе данных.        
        """
        response = requests.post(
            url=self.API_URL,
            json=self.test_user
        )
        assert response.status_code == 201

        connection = psycopg2.connect(self.DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (self.test_user["email"],))
        user = cursor.fetchone()
        print(user)
        connection.close()

        assert user is not None
        assert user[1] == self.test_user["username"]
        assert user[2] == self.test_user["email"]


    #если нужно удалять пользователя после теста
    def teardown_method(self):
        """_summary_
        Функция выполняется после каждого теста.
        Удаляет тестового пользователя из базы данных.
        """
        connection = psycopg2.connect(self.DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE email = %s", (self.test_user["email"],))
        connection.commit()
        cursor.close()
        connection.close()