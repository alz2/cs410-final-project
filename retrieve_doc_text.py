import json
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from time import gmtime, strftime

#import urllib.request ## urllib request does not get javascript webpages


# https://www.quora.com/How-can-I-extract-only-text-data-from-HTML-pages
# https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python


if len(sys.argv) != 2:
    raise ValueError('python3 retrieve_doc_text.py {PROF->PAPER_URL json}')

save_file_title ="data/papers_" + strftime("%Y-%m-%d_%H-%M-%S", gmtime()) + ".json"


def save_file():
    out_file_name = save_file_title
    json_str = json.dumps(prof_papers)
    with open(out_file_name, "w+") as outfile: # truncate aka rewrite
        outfile.write(json_str)
    outfile.close()

def extract_text_from_soup(soup):
    # https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
    # kill all script and style elements
    if soup is None:
        return ""

    for script in soup(["script", "style", "iframe", "img"]):
        script.extract()    # rip it out

    # get text
    if soup.body is not None:
        text = soup.body.get_text() # could do soup.body.get_text if don't want to extract head
    else:
        text = soup.get_text()

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
    else: # try to get the end of the word
        try:
            end_of_word = text.index(' ', 5000)
        except ValueError: # this happens to be the last word!
            return text

        res = text[ : end_of_word ] # cut text corpus off
    return res 




with open(sys.argv[1], 'r') as infile:

    driver = webdriver.PhantomJS() # browser
    driver.set_page_load_timeout(30) # 30 second timeout per page
    prof_papers = json.load(infile)
    processed = 0
    pdfs = 0

    for prof in prof_papers:
        papers = prof_papers[prof]
        for paper_info in papers:

            if len(paper_info) > 3:
                raise ValueError(str(paper_info) + ' has more than 3 elems... INVALID JSON')

            if len(paper_info) < 2: # this shouldn't happen but there seems to be some data inside the json which do not have links?
                continue

            if len(paper_info) == 3 and len(paper_info[2]) != 0: # already processed with no errors
                processed += 1 
                continue

            paper_link = paper_info[1]
            ending = paper_link[len(paper_link) - 4 : ]
            if ending == ".pdf" or ending == "=pdf": # pdf
                pdfs += 1
            else: # html
                try:
                    print(prof, paper_link)
                    driver.get(paper_link)
                except:
                    paper_info.append("")
                    prof_papers[prof] = papers
                    continue

                time.sleep(2) # sleep for 2 seconds hopefully thats enough for js to render on page
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                #
                # OKAY GOOD CONNECTION AND EVERYTHING WENT WELL
                #

                res = extract_text_from_soup(soup)
                if len(paper_info) == 3:
                    paper_info[2] = res
                else:
                    paper_info.append(res)
                #print(paper_info)

                processed += 1
                print("RETRIEVED DOCS ", processed)
                if processed % 50 == 0: # save every 50
                    save_file()

        save_file() 

infile.close()


