import urllib
from urllib import request, parse
from urllib.parse import urlparse
import time
import socket
from db_controller import DatabaseController

class Crawler:
    def __init__(self, project_name, timeout, web_driver_location, thread_instance, database_controller):
        self.project_name = project_name
        self.instance = thread_instance
        self.timeout = timeout
        self.web_driver_location = web_driver_location
        self.db_controller = database_controller

    def IsSpiderTrap(self, url):
        return True if "mailto:" or "tel:" in url or len(url) > 1000 else False

    def GetDomainAndIP(self, url):
        domain = urllib.parse.urlparse(url).netloc
        try:
            IP = socket.gethostbyname(domain)
        except socket.gaierror:
            IP = None
        return domain, IP

    def GetRobotsTxt(self, domain):
        url = "http://{}/robots.txt".format(domain)
        response = urllib.request.urlopen(url)
        return response.read().decode("utf-8")

    def GetRobotsContent(self, domain):
        # TODO: Timer for accesing robots txt
        # Check if Robots.txt is already in container:
        robots_txt = self.db_controller.DatabaseController.get_robots_txt(domain)
        if robots_txt is None:
            # Container with current domain does not have robots.txt so get it and insert it
            robots_content = self.GetRobotsTxt(domain)
            if robots_content is not None:
                self.db_controller.DatabaseController.insert_robots_txt(domain, robots_content)
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


    def StopCrawler(self):
        pass
