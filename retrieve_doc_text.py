import json
import sys
from bs4 import BeautifulSoup
import urllib.request


# https://www.quora.com/How-can-I-extract-only-text-data-from-HTML-pages

if len(sys.argv) != 2:
    raise ValueError('provide a file pls')
def save_file():
    out_file_name = 'DOCSINCLUDED_test.json'
    json_str = json.dumps(prof_papers)
    with open(out_file_name, "w+") as outfile: # truncate aka rewrite
        outfile.write(json_str)
    outfile.close()


with open(sys.argv[1]) as infile:
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
                    conn = urllib.request.urlopen(paper_link, timeout=60)
                except:
                    paper_info.append("")
                    prof_papers[prof] = papers
                    continue

                if conn is None: # connection failed... Content is empty string
                    paper_info.append("")
                    prof_papers[prof] = papers
                    continue
                else: # check the code
                    resp_code = conn.getcode()
                    if resp_code != 200: # only move foreward with 200's
                        papers.append("")
                        prof_papers[prof] = papers
                        continue

                soup = BeautifulSoup(conn, 'html.parser')

                #
                # OKAY GOOD CONNECTION AND EVERYTHING WENT WELL
                #

                # kill all script and style elements
                for script in soup(["script", "style"]):
                    script.extract()    # rip it out

                # get text
                text = soup.get_text() # could do soup.body.get_text if don't want to extract head

                # break into lines and remove leading and trailing space on each
                lines = (line.strip() for line in text.splitlines())
                # break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # drop blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                text = text.replace('\n', ' ') # replace new lines with spaces

                # only grabbing 1000 chars respecting word boundaries
                if len(text) <= 1000:
                    res = text
                else:
                    res = text[ : text.index(' ', 1000) ]
                # push back to 2'nd index
                paper_info.append(res)
                
                processed += 1
                print("RETRIEVED DOCS ", processed)
                if processed % 50 == 0: # save every 50
                    save_file()

        save_file() 

infile.close()


