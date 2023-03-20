import requests
import threading
import psycopg2
import urllib3
import concurrent.futures
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urldefrag

#Properties to use selenium for proper JS rendering
WEB_DRIVER_LOCATION = "webdriver/chromedriver.exe"
TIMEOUT = 5
chrome_options = Options()
chrome_options.add_argument("user-agent=fri-wier-spoders")
chrome_options.headless = True

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
        url = self.normalize_url(url)
        if ".gov.si" in url and not self.is_visited(url):
            self.frontier.append(url)

    def normalize_url(self, url):
        #Remove #
        url = urldefrag(url)[0]
        url = str(url)
        # Remove trailing slash.
        if url.endswith('/'):
            url = url[:-1]
        # Remove http://
        if url.startswith('http://'):
            url = url[7:]
        # Remove https://
        if url.startswith('https://'):
            url = url[8:]
        return url

    def print_frontier(self):
        print(self.frontier)

def crawler(frontier):
    driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)  
    while not frontier.is_empty():
        #Get URL from the frontier
        currentUrl = frontier.pop_element()
        #Retrieve page
        driver.get(currentUrl)
        # Timeout needed for Web page to render
        time.sleep(TIMEOUT)
        html = driver.page_source
        #Parsing links
        for element in driver.find_elements(By.TAG_NAME, 'a'):
            link = element.get_attribute("href")
            frontier.add_url(link)
        #print(frontier.print_frontier())

    driver.close()

if __name__ == '__main__':

    #Seed urls to frontier
    seed_urls = ['http://gov.si', 'http://evem.gov.si', 'http://e-uprava.gov.si', 'http://e-prostor.gov.si']
    frontier = Frontier(seed_urls)

    #Start crawler
    crawler(frontier)