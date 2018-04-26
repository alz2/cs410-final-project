import json
import sys
from bs4 import BeautifulSoup
import urllib.request

# https://www.quora.com/How-can-I-extract-only-text-data-from-HTML-pages

if len(sys.argv) != 2:
    raise ValueError('provide a file pls')


with open(sys.argv[1]) as infile:
    prof_papers = json.load(infile)
    for prof in prof_papers:
        papers = prof_papers[prof]
        for paper_info in papers:
            if len(paper_info) < 2:
                continue
            paper_link = paper_info[1]
            if paper_link[len(paper_link) - 4:] == ".pdf": # pdf
                print(paper_link)
            else: # html
                # https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
                if len(paper_info) >= 3:
                    continue
                try:
                    conn = urllib.request.urlopen(paper_link)
                except:
                    papers.append("")

                if conn is None: # connection failed... Content is empty string
                    papers.append("")
                    continue
                else: # check the code
                    resp_code = conn.getcode()
                    if resp_code != 200: # only move foreward with 200's
                        papers.append("")
                        continue

                soup = BeautifulSoup(conn, 'html.parser')
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
                papers.append(res)
 
    out_file_name = 'DOCSINCLUDED_' + sys.argv[1]
    json_str = json.dumps(prof_papers)
    with open(out_file_name, "w+") as outfile: # truncate aka rewrite
        outfile.write(json_str)
    outfile.close()

infile.close()


