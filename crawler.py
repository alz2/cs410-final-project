import urllib.request
from bs4 import BeautifulSoup

class Crawler:
    
    """
        Params:
            links -- list of links for the crawler to visit
            soup_analysis_fn -- function which takes in a BeautifulSoup as a parameter.
                                Once connection is made and html is parsed into a BeautifulSoup by crawler, soup_analysis_fn will be called on the soup
    """
    def __init__(self, links, soup_analysis_fn):
        self.links = links
        self.soup_analysis_fn = soup_analysis_fn 

    def crawl(self, timeout):
        """
            Visits each of self.links and calls self.soup_analysis_fn on parsed html
        """
        for l in self.links:
            conn = urllib.request.urlopen(l, timeout=timeout)
            if conn is None:
                print(l, "TIMEOUT")
                continue
            soup = BeautifulSoup(conn, "html.parser" )
            self.soup_analysis_fn(soup)
