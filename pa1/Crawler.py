import hashlib
import urllib
from urllib import request, parse
from urllib.parse import urlparse
import time
import socket
import re
from datetime import datetime

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

    def is_spider_trap(self, url):
        return True if "mailto:" in url or "tel:" in url or len(url) > 1000 else False
    
    def get_hash(self, html):
        return hashlib.sha256(html.encode("utf-8")).digest()
    
    def get_domain_and_ip(self, url):
        domain = urllib.parse.urlparse(url).netloc
        try:
            IP = socket.gethostbyname(domain)
        except socket.gaierror:
            IP = None
        return domain, IP

    def get_robots_txt_from_domain(self, domain):
        url = "http://{}/robots.txt".format(domain)
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode("utf-8")
        except:
            return
        
    def get_robots_content(self, domain):        
        # Check if Robots.txt is already in container:
        robots_txt = self.db_controller.get_robots_txt(domain)
        if robots_txt is None:
            print("robots.txt is not in container!")
            # Container with current domain does not have robots.txt so get it and insert it
            robots_txt = self.get_robots_txt_from_domain(domain)
            if robots_content is not None:
                print("Successfully retrived robots.txt!")                
                return robots_txt
            else:
                print("Current domain does not have robots.txt")
                return None
        return robots_txt

    def get_robot_allowed_paths(self, robots_txt):
        allowed_paths = []
        for line in robots_txt.split('\n'):
            line = line.strip()
            if line.startswith('Allow:'):
                allowed_path = line.split(':')[1].strip()
                allowed_paths.append(allowed_path)
        return allowed_paths

    def get_robot_disallowed_paths(self, robots_txt):
        disallowed_paths = []
        for line in robots_txt.split('\n'):
            line = line.strip()
            if line.startswith('Disallow:'):
                disallowed_path = line.split(':')[1].strip()
                disallowed_paths.append(disallowed_path)
        return disallowed_paths
 
    def get_sitemap(self, robots_txt):
        sitemap_urls = []
        for line in robots_txt.split('\n'):
            line = line.strip()
            if line.startswith('Sitemap:'):
                sitemap_url = re.findall(r'(https?://\S+)', line)[0]
                sitemap_urls.append(sitemap_url)
        return sitemap_urls
    
    def crawl_page(self, url):
        print("Crawling current page: " + url)

        if self.is_spider_trap(url):
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
        
        # Get domain and ip
        domain, ip = self.get_domain_and_ip(url)

        # Get robots.txt
        robots_content = self.get_robots_content(domain)

        if robots_content:
            allowed_paths = self.get_robot_allowed_paths(robots_content) # Not actually needed
            disallowed_paths = self.get_robot_disallowed_paths(robots_content)
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
                
        # Check if site is already in database
        status = self.db_controller.get_site(domain)

        # SITE DATABASE INSERTION
        
        if status == -1:
            # INSERT SITE INTO DATABASE
            if robots_content:
                sitemap = self.get_sitemap(robots_content)
                if sitemap is None:
                    print("Error cannot add site to container as the sitemap is not inside robots.txt")
                else:
                    self.db_controller.insert_site(domain, robots_content, sitemap[0])
                    # Tuki lahko se od sitemapa dodamo linke
        
        # PAGE DATABASE INSERTION
        page_type = "HTML"
        
        # Duplicat Checking
        page_hash = self.get_hash(url)
        if self.db_controller.is_duplicate(page_hash):
            html_content = ""
            page_type = "DUPLICATE"

        if content_type != "text/html":
            html_content = ""
            page_type = "BINARY"

        site_id = self.db_controller.get_site(domain)
        if site_id == -1:
            print("Internal error. Site must be valid in order to insert pages")

        accessedTime = datetime.now().isoformat()
        page_id = self.db_controller.insert_page(url=url, page_type_code=page_type, http_status_code=status_code, html_content=html_content, site_id=site_id, accessed_time=accessedTime)

        if page_id is None:
            print("Internal error. Page already exists!")

        # Insert HASH
        self.db_controller.insert_hash(page_hash, page_id)                 
      
        # Parsing links
        for element in self.web_driver.find_elements(By.TAG_NAME, 'a'):
            link = element.get_attribute("href")
            self.frontier.add_url(link)        

    def StopCrawler(self):
        self.web_driver.close()
        self.db_controller.close()
