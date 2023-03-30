import time
from urllib.parse import urldefrag

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from url_normalize import url_normalize

from webdriver_manager.chrome import ChromeDriverManager

from db_controller import DatabaseController

# Properties to use selenium for proper JS rendering
TIMEOUT = 5
chrome_options = Options()
chrome_options.add_argument("user-agent=fri-wier-spoders")
chrome_options.add_argument("--headless")


class Frontier:
    def __init__(self, seed):
        self.frontier = list(seed)
        self.visited = set()

    def is_empty(self):
        return len(self.frontier) == 0

    def pop_element(self):
        element = self.frontier.pop()
        self.mark_visited(element)
        return element

    def mark_visited(self, url):
        self.visited.add(url)

    def is_visited(self, url):
        if url in self.visited:
            return True
        else:
            return False

    def add_url(self, url):
        if url is not None:
            url = self.normalize_url(url)
            if url not in self.frontier and ".gov.si" in url and not self.is_visited(url):
                self.frontier.append(url)

    def normalize_url(self, url):
        url = url_normalize(url)
        # Remove #
        url = urldefrag(url)[0]
        url = str(url)
        # Remove trailing slash.
        if url.endswith('/'):
            url = url[:-1]
        return url

    def print_frontier(self):
        print(self.frontier)

def crawler(frontier):
    db_controller = DatabaseController()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    while not frontier.is_empty():
        # Get URL from the frontier
        current_url = frontier.pop_element()
        
        # Fetch URL to crawler and start crawling page: 
        
        # Retrieve page
        driver.get(current_url)
        # Timeout needed for Web page to render
        time.sleep(TIMEOUT)
        html = driver.page_source
        db_controller.insert_page(url=current_url, page_type_code='HTML', http_status_code=200)

        # Parsing links
        for element in driver.find_elements(By.TAG_NAME, 'a'):
            link = element.get_attribute("href")
            frontier.add_url(link)
        # print(frontier.print_frontier())

    db_controller.print_pages()
    driver.close()
    db_controller.close()


if __name__ == '__main__':
    # Seed urls to frontier
    seed_urls = ['http://gov.si', 'http://evem.gov.si', 'http://e-uprava.gov.si', 'http://e-prostor.gov.si']
    frontier = Frontier(seed_urls)
    # Start crawler
    crawler(frontier)
