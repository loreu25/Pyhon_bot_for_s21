import psycopg2

# Настройки подключения
DB_HOST = "localhost"  # Хост, где работает PostgreSQL
DB_NAME = "flags_db"  # Имя вашей базы данных
DB_USER = "root"  # Пользователь PostgreSQL
DB_PASSWORD = "root"  # Пароль пользователя
DB_PORT = 4545  # Порт (обычно 5432)

def add_to_flags(nickname, category):
    try:
        # Устанавливаем соединение с базой данных
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = connection.cursor()

        query = "INSERT INTO flags (nickname, category) VALUES (%s, %s);"
        cursor.execute(query, (nickname, category))
        connection.commit()
        print(f"Ник '{nickname}' добавлен в категорию '{category}'!")

        cursor.close()
        connection.close()
        print("Соединение с базой данных закрыто.")
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")


def find_peer(nickname):
    try:
        # Устанавливаем соединение с базой данных
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )

        cursor = connection.cursor()
        query = "SELECT category FROM flags WHERE nickname = %s;"
        cursor.execute(query, (nickname,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if result:
            return result[0]
        else:
            print(f"Сообщение от пользователя")
            return None
    except Exception as e:
        print(f"Ошибка при поиске категории: {e}")
        return None


def get_all_flags():
    with psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nickname, category FROM flags")
            rows = cursor.fetchall()
            return [{"id": row[0], "nickname": row[1], "category": row[2]} for row in rows]