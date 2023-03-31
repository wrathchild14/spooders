import threading
import psycopg2

lock = threading.Lock()


class DatabaseController:
    def __init__(self, host="localhost", user="user", password="SecretPassword"):
        self.connection = psycopg2.connect(host=host, user=user, password=password)
        self.connection.autocommit = True

    # TABLE SITE

    def insert_site(self, domain, robots_content, sitemap_content):
        with lock:
            cur = self.connection.cursor()
            cur.execute("INSERT INTO crawldb.site(domain, robots_content, sitemap_content)"
                        "VALUES (%s, %s, %s)", (domain, robots_content, sitemap_content))

            print(f"Log: inserted site with {domain} domain into database")
            cur.close()

    def get_site(self, domain):
        with lock:
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
        with lock:
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

    # TABLE PAGE

#     def insert_page(self, url, page_type_code, http_status_code, html_content):
#         with lock:
#             cur = self.connection.cursor()
#             cur.execute("INSERT INTO crawldb.page(url, page_type_code, html_content, http_status_code,accessed_time)"
#                         "VALUES (%s, %s, %s, %s, now())", (url, page_type_code, html_content, http_status_code))

#             print(f"Log: inserted page {url} with {page_type_code} type and {http_status_code} status into database")
#             cur.close()

    def insert_page(self, url, page_type_code, http_status_code, html_content, site_id, accessed_time):
        with lock:
            cur = self.connection.cursor()
            # cur.execute("INSERT INTO crawldb.page(url, page_type_code, html_content, http_status_code,accessed_time, site_id)"
            #             "VALUES (%s, %s, %s, %s, %s, %s)", (url, page_type_code, html_content, http_status_code, accessed_time, site_id)
            #             )
            cur.execute(
                "INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time) VALUES ((SELECT id FROM crawldb.site WHERE id=%s),(SELECT code FROM crawldb.page_type WHERE code=%s),%s,%s,%s,%s) RETURNING id;",
                (site_id, page_type_code, url, html_content, http_status_code, accessed_time)
            )
            print(f"Log: inserted page {url} with {page_type_code} type and {http_status_code} status into database")
            result = cur.fetchall()
            page_id = None
            if result:
                page_id = result[0][0]
            cur.close()
            return page_id

    def print_pages(self):
        print(f"Log: Pages got from database")
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM crawldb.page")
        fetched_pages = cur.fetchall()
        for page in fetched_pages:
            print(page)

    # TABLE PAGE_DATA

    def insert_page_data(self, page_id, data_type_code, data):
        with lock:
            cur = self.connection.cursor()
            cur.execute("INSERT INTO crawldb.page_data(page_id, data_type_code, data)"
                        "VALUES (%s, %s, %s)", (page_id, data_type_code, data))

            print(f"Log: inserted page_data for page {page_id} and {data_type_code} code into database")
            cur.close()

    # TABLE IMAGE

    def insert_image(self, page_id, filename, content_type, data, accessed_time):
        with lock:
            cur = self.connection.cursor()
            cur.execute("INSERT INTO crawldb.image(page_id, filename, content_type, data, accessed_time)"
                        "VALUES (%s,%s,%s,%s,%s)", (page_id, filename, content_type, data, accessed_time))

            print(f"Log: inserted image {filename} with {content_type} type into database")
            cur.close()

    # TABLE LINK

    def insert_link(self, from_page, to_page):
        with lock:
            cur = self.connection.cursor()
            cur.execute("INSERT INTO crawldb.link(from_page, to_page)"
                        "VALUES (%s,%s)", (from_page, to_page))

            print(f"Log: inserted link with from_page {from_page} and to_page {to_page} into database")
            cur.close()
    
    # HASHING CODE
    
    def is_duplicate(self, page_hash):
        with lock:
            cur = self.connection.cursor()
            cur.execute(
                "SELECT page_id FROM crawldb.hash WHERE hash=%s LIMIT 1;",
                (page_hash,)
            )
            status = False
            result = cur.fetchall()
            if result:
                status = True
            cur.close()
            return status

    def insert_hash(self, page_id, page_hash):
        with lock:
            cur = self.connection.cursor()
            cur.execute(
                "INSERT INTO crawldb.hash (page_id, hash) VALUES ((SELECT id FROM crawldb.page WHERE id=%s),%s);",
                (page_id, page_hash)
            )
            cur.close()
            return
    
    # CLOSE CONNECTION
    
    def close(self):
        self.connection.close()

    def url_exists(self, url):
        with lock:
            cur = self.connection.cursor()
            cur.execute("SELECT EXISTS(SELECT 1 from crawldb.page WHERE url=%s);", (url,))
            result = cur.fetchall()[0][0]
            cur.close()
            return result


# Usage
if __name__ == '__main__':
    database = DatabaseController()
    database.insert_page('http://evem.gov.si', "FRONTIER", 200)
    database.close()
