import urllib
from urllib import request, parse
from urllib.parse import urlparse
import time
import socket

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

from db_controller import DatabaseController

# Properties to use selenium for proper JS rendering
chrome_options = Options()
chrome_options.add_argument("user-agent=fri-wier-spoders")
chrome_options.add_argument("--headless")

class Crawler:
    def __init__(self, project_name, timeout, thread_instance, frontier):
        self.project_name = project_name
        self.instance = thread_instance
        self.timeout = timeout
        self.web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.db_controller = DatabaseController()
        self.frontier = frontier

    def IsSpiderTrap(self, url):
        return True if "mailto:" in url or "tel:" in url or len(url) > 1000 else False

    def GetDomainAndIP(self, url):
        domain = urllib.parse.urlparse(url).netloc
        try:
            IP = socket.gethostbyname(domain)
        except socket.gaierror:
            IP = None
        return domain, IP

    def GetRobotsTxt(self, domain):
        url = "http://{}/robots.txt".format(domain)
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode("utf-8")
        except:
            return
        
    def GetRobotsContent(self, domain):
        # TODO: Timer for accesing robots txt
        # Check if Robots.txt is already in container:
        robots_txt = self.db_controller.get_robots_txt(domain)
        if robots_txt is None:
            # Container with current domain does not have robots.txt so get it and insert it
            robots_content = self.GetRobotsTxt(domain)
            if robots_content is not None:
                self.db_controller.insert_site(domain, robots_content)
                return robots_content
            else:
                print("Current domain does not have robots.txt")
                return None
        return robots_txt

    def GetRobotAllowedPaths(self, robots_txt):
        allowed_paths = []
        for line in robots_txt.split('\n'):
            line = line.strip()
            if line.startswith('Allow:'):
                allowed_path = line.split(':')[1].strip()
                allowed_paths.append(allowed_path)
        return allowed_paths

    def GetRobotDisallowedPaths(self, robots_txt):
        disallowed_paths = []
        for line in robots_txt.split('\n'):
            line = line.strip()
            if line.startswith('Disallow:'):
                disallowed_path = line.split(':')[1].strip()
                disallowed_paths.append(disallowed_path)
        return disallowed_paths

    def CrawlPage(self, url):
        print("Crawling current page: " + url)

        if self.IsSpiderTrap(url):
            print("Spider trap detected, exiting URL...")
            return

        try:
            with urllib.request.urlopen(url) as response:
                time.sleep(self.timeout)
                status_code = response.getcode()
                info = response.info()
                content_type = info.get_content_type()
        except:
            print("Website cannot be reached!")
            return

        domain, ip = self.GetDomainAndIP(url)

        # Get robots.txt
        robots_content = self.GetRobotsContent(domain)

        if robots_content:
            allowed_paths = self.GetRobotAllowedPaths(robots_content) # Not needed
            disallowed_paths = self.GetRobotDisallowedPaths(robots_content)
            parsed_url = urlparse(url)
            for path in disallowed_paths:
                if parsed_url.path.startswith(path):
                    print("URL is not allowed by robots.txt")
                    return

        # Retrieve page
        self.web_driver.get(url)
        # Timeout needed for Web page to render
        time.sleep(self.timeout)
        html = self.web_driver.page_source
        
        self.db_controller.insert_page(url=url, page_type_code='HTML', http_status_code=200)
        
        # Parsing links
        for element in self.web_driver.find_elements(By.TAG_NAME, 'a'):
            link = element.get_attribute("href")
            self.frontier.add_url(link)
        self.frontier.print_frontier()

    def StopCrawler(self):
        self.web_driver.close()
        self.db_controller.close()
