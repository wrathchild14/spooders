import threading
import psycopg2

lock = threading.Lock()


class DatabaseController:
    def __init__(self, host: str = "localhost", user: str = "user", password: str = "SecretPassword"):
        self.connection = psycopg2.connect(host=host, user=user, password=password)
        self.connection.autocommit = True

    # TABLE SITE

    def insert_site(self, domain: str, robots_content: str = '', sitemap_content: str = ''):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO crawldb.site(domain, robots_content, sitemap_content)"
                    "VALUES (%s, %s, %s)", (domain, robots_content, sitemap_content))

        print(f"Log: inserted site with {domain} domain into database")
        cur.close()

    def get_site(self, domain):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT * FROM crawldb.site WHERE domain=%s;",
            (domain,)
        )
        # Check if array is empty, meaning we didn't find the site already present in the table
        site_id = -1
        result = cur.fetchall()
        if result:
            site_id = result[0][0]

        cur.close()
        return site_id

    def get_robots_txt(self, domain):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT robots_content FROM crawldb.site WHERE domain=%s;",
            (domain,)
        )
        # Check if array is empty, meaning we didn't find the site already present in the table
        robots = None
        result = cur.fetchall()
        if result:
            robots = result[0][0]

        cur.close()
        return robots
        
    # Obsolete
    # def insert_robots_txt(self, domain, robots_content):
    #     cur = self.connection.cursor()
    #     cur.execute(
    #         "INSERT INTO crawldb.site (domain, robots_content) VALUES (%s, %s)",
    #         (domain, robots_content)
    #     )
    #     self.connection.commit()
    #     cur.close()

    # TABLE PAGE

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

    # TABLE PAGE_DATA

    def insert_page_data(self, page_id, data_type_code, data):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO crawldb.page_data(page_id, data_type_code, data)"
                    "VALUES (%s, %s, %s)", (page_id, data_type_code, data))

        print(f"Log: inserted page_data for page {page_id} and {data_type_code} code into database")
        cur.close()

    # TABLE IMAGE

    def insert_image(self, page_id, filename, content_type, data, accessed_time):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO crawldb.image(page_id, filename, content_type, data, accessed_time)"
                    "VALUES (%s,%s,%s,%s,%s)", (page_id, filename, content_type, data, accessed_time))

        print(f"Log: inserted image {filename} with {content_type} type into database")
        cur.close()

    # TABLE LINK

    def insert_link(self, from_page, to_page):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO crawldb.link(from_page, to_page)"
                    "VALUES (%s,%s)", (from_page, to_page))

        print(f"Log: inserted image {filename} with {content_type} type into database")
        cur.close()

    # CLOSE CONNECTION
    
    def close(self):
        self.connection.close()


# Usage
if __name__ == '__main__':
    database = DatabaseController()
    database.insert_page('http://evem.gov.si', "FRONTIER", 200)
    database.close()
