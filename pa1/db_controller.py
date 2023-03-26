import threading
import psycopg2

lock = threading.Lock()


class DatabaseController:
    def __init__(self, host: str = "localhost", user: str = "user", password: str = "SecretPassword"):
        self.connection = psycopg2.connect(host=host, user=user, password=password)
        self.connection.autocommit = True

    def insert_page(self, url: str, page_type_code: str, http_status_code: int, html_content: str = ''):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO crawldb.page(url, page_type_code, html_content, http_status_code,accessed_time)"
                    "VALUES (%s, %s, %s, %s, now())", (url, page_type_code, html_content, http_status_code))

        print(f"Log: inserted page {url} with {page_type_code} type and {http_status_code} status into database")
        cur.close()

    def print_pages(self):
        print(f"Log: Pages got from database")
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM crawldb.page")
        fetched_pages = cur.fetchall()
        for page in fetched_pages:
            print(page)

    def close(self):
        self.connection.close()


# Usage
if __name__ == '__main__':
    database = DatabaseController()
    database.insert_page('http://evem.gov.si', "FRONTIER", 200)
    database.close()
