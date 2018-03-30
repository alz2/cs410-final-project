import urllib.request
from bs4 import BeautifulSoup

class Crawler:
    
    """
    Constructor 1:
    Use this if you have a fixed list of links to crawl
        Params:
            links 
                -- list of links for the crawler to visit
            soup_analysis_fn 
                -- function which takes in a BeautifulSoup as a parameter.
                -- Once connection is made and html is parsed into a BeautifulSoup by crawler
                   soup_analysis_fn will be called on the soup
    """
    def __init__(self, links, soup_analysis_fn):
        self.links = links
        self.soup_analysis_fn = soup_analysis_fn 
        self.visited = set()

    """
    Constructor 1:
    Use this if you have a dynamic list of links to crawl. Call (your_crawler).push_links_front(your_link)
    in a function and then set that function as the crawler soup_analysis_fn
        Params:
            links 
                -- initial list of links for the crawler to visit
        
    """
    def __init__(self, links):
        self.links = links
        self.soup_analysis_fn = None
        self.visited = set()

    def crawl(self, timeout):
        """
            Visits each of self.links and calls self.soup_analysis_fn on parsed html
        """
        while len(self.links) != 0:
            l = self.links.pop()

            if l in self.visited: # don't repeate links
                continue

            conn = urllib.request.urlopen(l, timeout=timeout)
            if conn is None:
                print(l, "TIMEOUT")
                continue

            self.visited.add(l);
            soup = BeautifulSoup(conn, "html.parser" )
            
            if self.soup_analysis_fn is not None:
                self.soup_analysis_fn(soup)

    """
        Pushes link to front of the queue
    """
    def push_links_front(self, link):
        self.links.append(link)
