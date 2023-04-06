import time
# from urllib.parse import urldefrag
import threading

# from url_normalize import url_normalize

from Crawler import Crawler
from ProjectConfig import *
from db_controller import DatabaseController

"""
# Local frontier storage
class Frontier:
    def __init__(self, seed):
        self.frontier = list(seed)
        self.visited = set()

    def is_empty(self):
        return len(self.frontier) == 0

    def pop_element(self):
        element = self.frontier.pop(0)
        self.mark_visited(element)
        return element

    def mark_visited(self, url):
        self.visited.add(url)

    def is_visited(self, url):
        return url in self.visited

    def add_url(self, url):
        url = self.canon_url(url)
        if url is not None and "gov.si" in url and not self.is_visited(url):
            if url not in self.frontier:
                self.frontier.append(url)

    def canon_url(self, url):
        if url is None or url == "":
            return None
        if "javascript:" in url:
            return None
        if url[0] == "#":
            return None
        if url == "/":
            return None
        if url.startswith('https://'):
            url = url[8:]
        if url.startswith('http://'):
            url = url[7:]
        if url.startswith("www."):
            url = url[4:]
            url = "http://" + str(url)
        if not url.startswith('http://'):
            url = "http://" + str(url)
        # Remove #
        url = urldefrag(url)[0]
        url = str(url)
        # Normalize
        url = url_normalize(url)
        # Remove filtering
        if "?" in url:
            url = url.split("?")[0]
        # Remove trailing slash.
        if url.endswith('/'):
            url = url[:-1]
        return url

    def print_frontier(self):
        print(self.frontier)
"""

def crawler(thread_index, db_controller):
    # Create crawler
    crawler = Crawler(PROJECT_NAME, TIMEOUT, SERVER_TIMEOUT, thread_index, db_controller)

    while not db_controller.is_frontier_empty():
        # Get URL from the frontier
        page = db_controller.pop_frontier()
        if page != None:
            page_id = page[0]
            current_url = page[1]
            # Fetch URL to crawler and start crawling page:
            crawler.crawl_page(current_url, page_id)

    crawler.StopCrawler()


if __name__ == '__main__':
    db_controller = DatabaseController()

    # Seed urls to frontier
    seed_urls = SEED_URLS
    # Initialize frontier
    if db_controller.is_frontier_empty():
        # Insert seed pages
        for seed in seed_urls:
            db_controller.insert_frontier(url=seed)

    if NUMBER_OF_WORKERS > 1:
        # Create multiple workers in parallel
        workers = []
        for i in range(NUMBER_OF_WORKERS):
            worker = threading.Thread(target=crawler, args=(i, db_controller))
            # Start thread
            worker.start()
            workers.append(worker)
        
        # While frontier not empty, check for live threads and start more threads
        while True:
            for i in range(NUMBER_OF_WORKERS):
                workers[i].join(5.0)
                if not workers[i].is_alive():
                    # if thread no longer alive, remove from list of threads and create another
                    print("Log: restarting thread no. " + str(i))
                    restart_worker = threading.Thread(target=crawler, args=(i, db_controller))
                    restart_worker.start()
                    workers[i] = restart_worker

    else:
        crawler(0, db_controller)
