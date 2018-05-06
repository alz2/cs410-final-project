import scholarly
import json
from threading import Thread, Lock
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import tempfile
import time
import urllib.request
import PyPDF2
import os 


# Globals!
seen_mutex = Lock()
results_mutex = Lock()
errors_mutex = Lock()
dirpath = tempfile.TemporaryDirectory() # temporary directory which will be cleaned up automatically by garbege collection

# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------

"""
Given a soup object parsed by BeautifulSoup, extract around 5000 chars 
respecting word boundaries from the texts of the htmls
Args:
    soup -- BeautifulSoup parsed html/connection
Return:
    String of text
"""
def extract_text_from_soup(soup):
    # https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
    # kill all script and style elements
    if soup is None:
        return ""

    for script in soup(["script", "style", "iframe", "img"]):
        script.extract()    # rip it out

    # get text
    if soup.body is not None:
        text = soup.body.get_text() # or soup.get_text()
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


"""
Given a url string determine whether or not it represents a pdf
Args:
    link -- string url
Return:
    True/False
"""
def is_pdf(link):
    if len(link) < 4:
        return False
    ending = link[len(link) - 4 : ]
    return ending == ".pdf" or ending == "=pdf" # pdf


"""
Downloads pdf from link as 'name' in directory 'dirpath'
Args:
    link -- url of pdf
    name -- name to save pdf as
    dirpath -- path to the save directory
Return:
    String path to the pdf
"""
def retrive_pdf(link, name, dirpath):
    fullname = dirpath + '/' + name
    try:
        urllib.request.urlretrieve(link, fullname)
    except:
        return ""
    return fullname


"""
Extracts around 5000 chars respecting word boundaries from pdf
Args:
    fullname -- full path to pdf
Return:
    String result
"""
def extract_text_from_pdf(fullname):
    f = open(fullname, 'rb') 
    try:
        pdfReader = PyPDF2.PdfFileReader(f) # open file
        file_pages = pdfReader.numPages
    except: # error :(
        f.close()
        os.remove(fullname)
        return ""

    text = ""
    pg_ct = 0
    try:
        while pg_ct < file_pages and len(text) < 5000: # 5000 chars
            pageObj = pdfReader.getPage(pg_ct)
            page_text = pageObj.extractText().strip()
            text += page_text + " " # safety space for pages
            pg_ct += 1
    except:
        pass

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text = text.replace('\n', ' ') # replace new lines with spaces

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


"""
Helper function to make sure document text is added to right index
"""
def insert_doc_text(paper_info, doc_text):
    if len(paper_info) == 2:
        paper_info.append(doc_text)
    if len(paper_info) == 3:
        paper_info[2] = doc_text


"""
Retrieves the document text of a paper_info list. Modifies paper_info.
Args:
    paper_info -- [NAME_OF_PAPER, LINK, <optional>""]
    driver -- selenium webdriver used to retrieve html results
"""
def retrieve_doc_text(paper_info, driver):
    link = paper_info[1]
    print(link)
    if is_pdf(link): # pdf
        fullname = retrive_pdf(link, paper_info[0] + '.pdf', dirpath.name)
        if len(fullname) != 0:
            res = extract_text_from_pdf(fullname)
            insert_doc_text(paper_info, res)
        else: # something went wrong
            insert_doc_text(paper_info, "") 
    else: # html
        try:
            driver.get(link)
        except TimeoutException: # timeout error 
            insert_doc_text(paper_info, "")
            return 

        time.sleep(2) # sleep for 2 seconds hopefully thats enough for js to render on page
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        #
        # OKAY GOOD CONNECTION AND EVERYTHING WENT WELL
        #

        res = extract_text_from_soup(soup)
        insert_doc_text(paper_info, res)


"""
Helper function for threads. This is basically the main retrieval method
"""
def _worker_paper_retrieve(author_publications, prof, results, errors, seen, driver):
    for p in author_publications:
        if p.bib['title'] not in seen: # have not seen the paper-- must retrieve URL
            pub_filled = p.fill() # get more information about publication
            bib = pub_filled.bib
            if 'url' in bib: # could find the URL?
                pi = [bib['title'], bib['url']]
                retrieve_doc_text(pi, driver) # grab the doc text
                # new paper_info! append to dict
                results_mutex.acquire()
                try:
                    results[prof].append(pi)
                finally:
                    results_mutex.release()
            else:
                # add to errors and move on
                results_mutex.acquire()
                try:
                    errors[prof].append(bib['title'])
                finally:
                    results_mutex.release()
                continue
        else: # url has already been retrieved
            pi = seen[p.bib['title']] 
            if len(pi) == 3 and len(pi[2]) != 0: # no need to do anything
                continue
            # retrieve doc text since url has been retrieved, should reflect in list cuz mutable
            retrieve_doc_text(pi, driver)


"""
Helper function to splti a list to n chunks
# https://stackoverflow.com/questions/2130016/splitting-a-list-into-n-parts-of-approximately-equal-length
"""
def splitnchunks(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


class PaperRetriever:

    """
        Constructor for the PaperRetriever:
        Args:
            professor_list: List of professor names
            history: a json dict of previously retrived dict of key=professor, value=[(title, link)]. 
                    Can be None if running without history
            num_threads: (default 1) Number of threads used to parse scholar... be careful of 503s
            save_as: file to the newly parsed json
            
    """
    def __init__(self, professor_list, save_as, history, num_threads=1):
        if professor_list is None:
            raise ValueError('Must provide a list of professors')

        self.professors = professor_list # list of professor names
        self.results = {} # dict of key=professor, value=[(title, link),...] for each paper
        self.seen_papers = {} # dict of key=professor, value=dict of key=paper name value=paper_infos
        self.errors = {}
        if save_as is None:
            raise ValueError('Must provide a save file')
        self.save_as = save_as
        self.num_threads = num_threads
        self.drivers = [] # create a webdriver for each thread
        for i in range(num_threads):
            d = webdriver.PhantomJS()
            d.set_page_load_timeout(30)
            self.drivers.append(d) # browser for client js rendered text

        # open and read previously retrieved links
        if history is not None:
            prior_file = open(history, "r");
            self.results = json.load(prior_file) # parse json
            # add to seen set to prevent re-retrieval
            for prof in self.results.keys():

                self.seen_papers[prof] = {}
                paper_infos = self.results[prof]
                for pi in paper_infos:
                    self.seen_papers[prof][pi[0]] = pi # map name of paper to whole paer info
            prior_file.close()


    """
        This function will go through self.professors and retrieve the url of each paper the PaperRetriever can find.
        The papers retrieved will be new -- that is it will not re-retrieve URLs for paper's it has already retrieved.

        After each paper from a professor is retrieved, the PaperRetriever will save the current results to self.save_as
        to prevent a crash from messing up the whole crawl.
    """
    def retrieve(self):
        for prof in self.professors:

            print("Retrieving Papers for", prof)

            if prof not in self.results:
                self.results[prof] = []
                self.errors[prof] = []

            if prof not in self.seen_papers:
                self.seen_papers[prof] = {} # create the per prof, papername->paperinfo dict

            # query scholar for author
            search_query = scholarly.search_author(prof) 
            try:
                author = next(search_query).fill()
            except StopIteration:
                # TODO HANDLE THIS CASE
                print(prof + " does not have a google scholar profile")
                continue

            # divide list of publications for threads
            author_publications = author.publications
            chunks = list(splitnchunks(author_publications, self.num_threads))

            # create and start threads
            t = []
            for i in range(self.num_threads):
                t.append(Thread(target=_worker_paper_retrieve, args=(chunks[i], prof, self.results, self.errors, self.seen_papers[prof], self.drivers[i])))
                t[i].start()

            # join threads
            for i in range(self.num_threads):
                t[i].join()

            # save the file
            self.save_results_as_json()
            self.save_errors_as_json()
        
        return self.results


    """
    Dump the contents of self.results into a self.save_as as json
    """
    def save_results_as_json(self):
        json_str = json.dumps(self.results)
        with open(self.save_as, "w+") as outfile: # truncate aka rewrite
            outfile.write(json_str)
        outfile.close()

    """
    Dump the contents of self.errors into ERRORS_<self.save_as> as json
    """
    def save_errors_as_json(self):
        json_str = json.dumps(self.errors)
        if len(json_str) != 0:
            err_file_name = "ERRORS_" + self.save_as 
            with open(err_file_name, "w+") as err_file:
                err_file.write(json_str)
            err_file.close()



