import json
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import tempfile
import time
import urllib.request
import PyPDF2
import os 

from time import gmtime, strftime

#import urllib.request ## urllib request does not get javascript webpages


# https://www.quora.com/How-can-I-extract-only-text-data-from-HTML-pages
# https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python


if len(sys.argv) != 2:
    raise ValueError('python3 retrieve_doc_text.py {PROF->PAPER_URL json}')


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


def is_pdf(link):
    if len(link) < 4:
        return False
    ending = link[len(link) - 4 : ]
    return ending == ".pdf" or ending == "=pdf" # pdf


def retrive_pdf(link, name, dirpath):
    fullname = dirpath + name
    try:
        urllib.request.urlretrieve(link, fullname)
    except:
        return ""
    return fullname


def extract_text_from_pdf(fullname):
    f = open(fullname, 'rb') 
    try:
        pdfReader = PyPDF2.PdfFileReader(f) # open file
    except: # error :(
        f.close()
        os.remove(fullname)
        return ""

    text = ""
    pg_ct = 0
    file_pages = pdfReader.numPages
    while pg_ct < file_pages and len(text) < 5000: # 5000 chars
        pageObj = pdfReader.getPage(pg_ct)
        page_text = pageObj.extractText().strip()
        text += page_text + " " # safety space for pages
        pg_ct += 1

    if len(text) > 5000:
        # trim to length
        try:
            end_of_word = text.index(' ', 5000)
            res = text[ : end_of_word ] # cut text corpus off
        except ValueError: # this happens to be the last word!
            res = text
    else:
        res = text
    
    f.close()
    # we don't need the file anymore
    os.remove(fullname)
    return res


def insert_doc_text(paper_info, doc_text):
    if len(paper_info) == 2:
        paper_info.append(doc_text)
    if len(paper_info) == 3:
        paper_info[2] = doc_text

#
# BEGIN MAIN CODE
#

save_file_title ="data/papers_" + strftime("%Y-%m-%d_%H-%M-%S", gmtime()) + ".json"

# make temp for downloading parsing pdf files. This dir will be cleaned up with garbage collection on POSIX systems
dirpath = tempfile.TemporaryDirectory()
print(dirpath.name)

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
                #processed += 1  for saving sakes commented out
                continue
            
            link = paper_info[1]
            print(prof, link)

            if is_pdf(link): # pdf
                pdfs += 1
                fullname = retrive_pdf(link, str(pdfs), dirpath.name)
                if len(fullname) != 0:
                    res = extract_text_from_pdf(fullname)
                    if len(res) != 0:
                        print('SUCCESS!')
                    insert_doc_text(paper_info, res)
                    processed += 1
                    print("RETRIEVED DOCS ", processed)
                    if processed % 50 == 0: # save every 50
                        save_file()

                else: # something went wrong
                    insert_doc_text(paper_info, "") 
            else: # html
                try:
                    driver.get(link)
                except: # timeout error 
                    insert_doc_text(paper_info, "")
                    continue

                time.sleep(2) # sleep for 2 seconds hopefully thats enough for js to render on page
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                #
                # OKAY GOOD CONNECTION AND EVERYTHING WENT WELL
                #

                res = extract_text_from_soup(soup)
                if len(res) != 0:
                    print('SUCCESS!')

                insert_doc_text(paper_info, res)
                #print(paper_info)

                processed += 1
                print("RETRIEVED DOCS ", processed)
                if processed % 50 == 0: # save every 50
                    save_file()

        save_file() 

infile.close()
