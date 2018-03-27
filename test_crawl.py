from crawler import Crawler

titles = []

# example analysis function -- for the project we may have to do inverted index calculations here
def print_soup_title(soup):
    titles.append(soup.title.string)
    print(soup.title.string)


# visit these links
links = ["https://www.google.com", "https://www.yahoo.com/"]
crawler = Crawler(links, print_soup_title)
crawler.crawl(20) # timeout 20 seconds


print("HERE IS YOUR COPY")
for t in titles:
    print(t)
