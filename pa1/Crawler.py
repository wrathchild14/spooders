import hashlib
import os
import urllib
from urllib import request, parse
from urllib.parse import urlparse, urljoin, urldefrag
from url_normalize import url_normalize
import time
import socket
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

# Properties to use selenium for proper JS rendering
chrome_options = Options()
chrome_options.add_argument("user-agent=fri-wier-spoders")
chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=1') # disables common info console logs

class Crawler:
    def __init__(self, project_name, timeout, server_timeout, thread_instance, db_controller):
        self.project_name = project_name
        self.instance = thread_instance
        self.timeout = timeout
        self.server_timeout = server_timeout
        self.web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.db_controller = db_controller

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
            print("Robots.txt is not in container!")
            # Container with current domain does not have robots.txt so get it and insert it
            robots_txt = self.get_robots_txt_from_domain(domain)
            if robots_txt is not None:
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

    def get_image_links(self, url, html_content, robots_content):
        disallowed_paths = set()
        if robots_content is not None:
            disallowed_paths = self.get_robot_disallowed_paths(robots_content)

        html = BeautifulSoup(html_content, 'html.parser')
        img_tags = html.find_all('img')
        img_links = []
        for img in img_tags:
            img_link = img.get('src')
            if img_link is not None and not any(path in img_link for path in disallowed_paths):
                img_links.append(urljoin(url, img_link))

        return img_links

    def check_accessed_time(self, domain_accessed_time, ip_accessed_time):
        domain_time_diff, ip_time_diff = timedelta(hours=1), timedelta(hours=1)
        if domain_accessed_time is not None:
            domain_time_diff = datetime.now() - domain_accessed_time
        if ip_accessed_time is not None:
            ip_time_diff = datetime.now() - ip_accessed_time
        if domain_time_diff <= timedelta(seconds=self.server_timeout) \
                or ip_time_diff <= timedelta(seconds=self.server_timeout):
            print("Timout: waiting for 1 second")
            time.sleep(1)
            self.check_accessed_time(domain_accessed_time, ip_accessed_time)

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

    def crawl_page(self, url, page_id):
        print("Crawling current page: " + url)

        # Get domain and ip
        domain, ip = self.get_domain_and_ip(url)
        self.check_accessed_time(self.db_controller.get_last_accessed_domain(domain),
                                 self.db_controller.get_last_accessed_ip_address(ip))

        try:
            with urllib.request.urlopen(url) as response:
                status_code = response.getcode()
                info = response.info()
                content_type = info.get_content_type()
                self.db_controller.update_site_last_accessed_time(domain, ip, datetime.now().isoformat())
        except:
            print("Website cannot be reached!")
            accessedTime = datetime.now().isoformat()
            self.db_controller.update_page(page_id=page_id, url=url, page_type_code=None, http_status_code=404,
                                                 html_content=None, site_id=None, accessed_time=accessedTime)
            return

        # Get robots.txt
        robots_content = self.get_robots_content(domain)

        if robots_content:
            allowed_paths = self.get_robot_allowed_paths(robots_content)  # Not actually needed
            disallowed_paths = self.get_robot_disallowed_paths(robots_content)
            parsed_url = urlparse(url)
            for path in disallowed_paths:
                if parsed_url.path.startswith(path):
                    print("URL is not allowed by robots.txt")
                    return

        # Check if site is already in database
        status = self.db_controller.get_site(domain)

        # SITE DATABASE INSERTION

        if status == -1:
            # INSERT SITE INTO DATABASE
            if robots_content:
                sitemap = self.get_sitemap(robots_content)
                if len(sitemap) == 0:
                    print("Error cannot add site to container as the sitemap is not inside robots.txt")
                    print("Adding empty sitemap")
                    self.db_controller.insert_site(domain, robots_content, "", ip, datetime.now().isoformat())
                else:
                    self.db_controller.insert_site(domain, robots_content, sitemap[0], ip, datetime.now().isoformat())
                    # Tuki lahko se od sitemapa dodamo linke
            else:
                # Site has no robots.txt add it anyway but with empty robots and sitemap
                self.db_controller.insert_site(domain, "", "", ip, datetime.now().isoformat())

        # Retrieve page
        try:
            self.web_driver.get(url)
        except: # Error occured while rendering page (SSL certificate error, timeout...)
            if content_type == "text/html":
                page_type = "HTML"
            else:
                page_type = "BINARY"
            accessedTime = datetime.now().isoformat()
            self.db_controller.update_page(page_id=page_id, url=url, page_type_code=page_type, http_status_code=500,
                                                 html_content=None, site_id=None, accessed_time=accessedTime)
            return
        """except WebDriverException:
            print(f"Exception: WebDriverException for {url}...")
            return
        except:
            print(f"Exception: default for {url}...")
            return"""

        # Timeout needed for Web page to render
        time.sleep(self.timeout)
        html_content = self.web_driver.page_source

        # PAGE DATABASE INSERTION
        page_type = "HTML"

        # Duplicate Checking
        page_hash = self.get_hash(html_content)
        [duplicate_status, duplicate_id] = self.db_controller.is_duplicate(page_hash)
        if duplicate_status:
            html_content = ""
            page_type = "DUPLICATE"

        if content_type != "text/html":
            html_content = ""
            page_type = "BINARY"

        site_id = self.db_controller.get_site(domain)
        if site_id == -1:
            # If this happens we should exit?
            print("Internal error. Site must be valid in order to insert pages")
            return

        accessedTime = datetime.now().isoformat()
        self.db_controller.update_page(page_id=page_id, url=url, page_type_code=page_type, http_status_code=status_code,
                                                 html_content=html_content, site_id=site_id, accessed_time=accessedTime)

        # Link page if duplicate
        if page_type == "DUPLICATE":
            self.db_controller.insert_link(page_id, duplicate_id[0])
            return # Skip processing since duplicate page already parsed

        # Insert HASH
        self.db_controller.insert_hash(page_id=page_id, page_hash=page_hash)

        # IMAGE INSERTION

        img_links = self.get_image_links(url, html_content, robots_content)
        if len(img_links) == 0:
            pass
        else:
            for image_url in img_links:
                extension = os.path.splitext(image_url)[1]
                file_name, ext = os.path.splitext(image_url)
                if len(file_name) > 255:
                    print("Error image link is too big to insert in database. Skipping image...")
                    continue
                if extension == ".PNG" or extension == ".png":
                    self.db_controller.insert_image(page_id, file_name, "PNG", b"None", accessedTime)
                elif extension == ".jpg" or extension == ".JPG" or extension == ".jpeg" or extension == ".JPEG":
                    self.db_controller.insert_image(page_id, file_name, "JPG", b"None", accessedTime)
                elif extension == ".GIF" or extension == ".gif":
                    self.db_controller.insert_image(page_id, file_name, "GIF", b"None", accessedTime)
        
        all_links = []
        # Parsing href links
        for element in self.web_driver.find_elements(By.TAG_NAME, 'a'):
            try:
                link = element.get_attribute("href")
                if link != None:
                    all_links.append(link)
            except:
                print(f"Exception: on {element} element")

        # Parsing onclick links
        for element in self.web_driver.find_elements(By.XPATH, "//*[@onclick]"):
            link = element.get_attribute("onclick")
            if "location.href" in link or "document.location" in link:
                link = link.split("=")[1].strip()
                # Extend relative URLs before adding to frontier
                if link.startswith("#") or link.startswith("/#"):
                    continue
                elif not link.startswith("http:") or not link.startswith("https:"):
                    link = urljoin(url, link)
                all_links.append(link)

        # Check for non-html content (.pdf, .doc, .docx, .ppt and .pptx) and insert to page_data table,
        # otherwise insert to frontier
        for link in all_links:
            if link.endswith(".pdf"):
                self.db_controller.insert_page_data(page_id, "PDF", b"None")
            elif link.endswith(".doc"):
                self.db_controller.insert_page_data(page_id, "DOC", b"None")
            elif link.endswith(".docx"):
                self.db_controller.insert_page_data(page_id, "DOCX", b"None")
            elif link.endswith(".ppt"):
                self.db_controller.insert_page_data(page_id, "PPT", b"None")
            elif link.endswith(".pptx"):
                self.db_controller.insert_page_data(page_id, "PPTX", b"None")
            else: # html content
                link = self.canon_url(link)
                if link is not None and "gov.si" in link and not self.is_spider_trap(link):
                    # Check if page already exists, otherwise insert
                    new_page = self.db_controller.get_page(link)
                    if new_page == -1:
                        new_page = self.db_controller.insert_frontier(url=link)
                    # Add links to link table
                    if page_id != new_page:
                        self.db_controller.insert_link(page_id, new_page)

    def StopCrawler(self):
        self.web_driver.close()
        self.db_controller.close()
