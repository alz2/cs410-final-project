import json
import sys
from bs4 import BeautifulSoup
from selenium import webdriver

#import urllib.request ## urllib request does not get javascript webpages


# https://www.quora.com/How-can-I-extract-only-text-data-from-HTML-pages
# https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python


if len(sys.argv) != 2:
    raise ValueError('provide a file pls')

def save_file():
    out_file_name = 'DOCSINCLUDED_test.json'
    json_str = json.dumps(prof_papers)
    with open(out_file_name, "w+") as outfile: # truncate aka rewrite
        outfile.write(json_str)
    outfile.close()

def extract_text_from_soup(soup):
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.body.get_text() # could do soup.body.get_text if don't want to extract head

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text = text.replace('\n', ' ') # replace new lines with spaces

    # only grabbing 1000 chars respecting word boundaries
    if len(text) <= 5000:
        res = text
    else:
        res = text[ : text.index(' ', 5000) ]
    return res 


with open(sys.argv[1]) as infile:

    driver = webdriver.PhantomJS() # browser
    driver.set_page_load_timeout(30) # 30 second timeout per page
    prof_papers = json.load(infile)
    processed = 0
    pdfs = 0

    for prof in prof_papers:
        papers = prof_papers[prof]
        for paper_info in papers:
            if len(paper_info) < 2:
                continue
            paper_link = paper_info[1]
            if paper_link[len(paper_link) - 4:] == ".pdf": # pdf
                pdfs += 1
            else: # html
                # https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
                if len(paper_info) >= 3:
                    continue
                try:
                    driver.get(paper_link)
                except:
                    paper_info.append("")
                    prof_papers[prof] = papers
                    continue

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                #
                # OKAY GOOD CONNECTION AND EVERYTHING WENT WELL
                #

                res = extract_text_from_soup(soup)
                paper_info.append(res)
                print(paper_info)

                processed += 1
                print("RETRIEVED DOCS ", processed)
                if processed % 50 == 0: # save every 50
                    save_file()

        save_file() 

infile.close()


