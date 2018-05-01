import sys
import json

if len(sys.argv) != 2:
    raise ValueError('Gimme file')

with open(sys.argv[1], 'r') as data_in:

    data = json.loads(data_in.read())

    prof_failures_dict = {}
    papers_total = 0
    links_total = 0
    content_total = 0
    content_errors = 0
    pdf_total = 0
    html_total = 0
    professors_total = 0

    for prof in data:
        prof_failures_dict[prof] = 0
        professors_total += 1
        papers = data[prof]
        for p_tup in papers:
            # see if its a pdf or link
            if len(p_tup) >= 2:
                paper_link = p_tup[1]
                ending = paper_link[len(paper_link) - 4 : ]
                if ending == ".pdf" or ending == "=pdf": # pdf
                    pdf_total += 1
                else:
                    html_total += 1

            papers_total += 1
            if len(p_tup) == 3: # content of doc

                if len(p_tup[2]) != 0:
                    content_total += 1 
                else:
                    content_errors += 1
                    prof_failures_dict[prof] += 1
                links_total += 1

            elif len(p_tup) == 2:
                links_total += 1 
            elif len(p_tup) > 3:
                print(str(p_tup) + 'HAS MORE THAN 3 ELEMS... INVALID JSON')

data_in.close()
print(professors_total, 'total professors')
print(papers_total, 'total papers')
print(pdf_total, 'were pdfs')
print(html_total, 'were webpages')
print(links_total, 'total links')
print(content_total, 'total documents parsed')
print(content_errors, 'HTML FAILURES')

print("######## ERRORS BY PROFESSOR #######")
print(prof_failures_dict)
