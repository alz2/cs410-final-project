from crawler import Crawler

titles = []

# visit these links
links = ["https://www.google.com", "https://www.yahoo.com"]
crawler = Crawler(links)

# example analysis function -- for the project we may have to do inverted index calculations here
def print_soup_title(soup):
    titles.append(soup.title.string)
    print(soup.title.string)
    crawler.push_links_front("https://docs.python.org/3.1/tutorial/datastructures.html")
    
crawler.soup_analysis_fn = print_soup_title;

crawler.crawl(20) # timeout 20 seconds


print("HERE IS YOUR COPY")
for t in titles:
    print(t)
