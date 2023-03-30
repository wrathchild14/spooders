import time
from urllib.parse import urldefrag

from url_normalize import url_normalize

from Crawler import Crawler
from ProjectConfig import *

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
        if url in self.visited:
            return True
        else:
            return False

    def add_url(self, url):
        url = self.canon_url(url)
        if url != None and ".gov.si" in url and not self.is_visited(url):
            self.frontier.append(url)

    def canon_url(self, url):
        if url == None or url == "":
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

if __name__ == '__main__':
    # Seed urls to frontier
    seed_urls = SEED_URLS
    frontier = Frontier(seed_urls)

    # Start crawler
    crawler = Crawler(PROJECT_NAME, TIMEOUT, 0, frontier)

    while not frontier.is_empty():
        # Get URL from the frontier
        current_url = frontier.pop_element()        
        # Fetch URL to crawler and start crawling page:
        crawler.CrawlPage(current_url)

    crawler.StopCrawler()