import psycopg2


def reset_db():
    connection = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    connection.autocommit = True

    cursor = connection.cursor()

    # cur.execute("TRUNCATE TABLE crawldb.site RESTART IDENTITY CASCADE")
    cursor.execute("TRUNCATE TABLE crawldb.page RESTART IDENTITY CASCADE")
    # cur.execute("TRUNCATE TABLE crawldb.link CASCADE")
    # cur.execute("TRUNCATE TABLE crawldb.image RESTART IDENTITY CASCADE")
    # cur.execute("TRUNCATE TABLE crawldb.page_data RESTART IDENTITY CASCADE")

    print("Log: successfully reset tables")

    cursor.close()
    connection.close()


if __name__ == '__main__':
    reset_db()
