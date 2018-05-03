import sys
import json

if len(sys.argv) != 2:
    raise ValueError('Gimme file')

with open(sys.argv[1], 'r') as data_in:

    data = json.loads(data_in.read())

    prof_failures_dict = {}
    papers_total = 0
    links_total = 0
    pdf_total = 0
    professors_total = 0
    html_total = 0

    html_parsed = 0
    html_errs = 0

    pdf_parsed = 0
    pdf_errs = 0

    for prof in data:

        prof_failures_dict[prof] = 0
        professors_total += 1
        papers = data[prof]

        for p_tup in papers:
            papers_total += 1

            entries = len(p_tup)
            # see if its a pdf or link
            if entries < 2: # can't get information
                continue

            paper_link = p_tup[1]
            ending = paper_link[len(paper_link) - 4 : ]
            if ending == ".pdf" or ending == "=pdf": # pdf
                pdf_total += 1
                if entries == 3: # entry for doc content

                    if len(p_tup[2]) != 0:
                        pdf_parsed += 1 
                    else:
                        pdf_errs += 1
                        prof_failures_dict[prof] += 1

                if entries > 3:
                    print(str(p_tup) + 'HAS MORE THAN 3 ELEMS... INVALID JSON')

                if entries == 2: # no content!
                    pdf_errs += 1


            else: # html
                html_total += 1
                if entries == 3: # entry for doc content

                    if len(p_tup[2]) != 0:
                        html_parsed += 1 
                    else:
                        html_errs += 1
                        prof_failures_dict[prof] += 1

                if entries > 3:
                    print(str(p_tup) + 'HAS MORE THAN 3 ELEMS... INVALID JSON')

                if entries == 2: # no content!
                    html_errs += 1

            links_total += 1

data_in.close()
print(professors_total, 'total professors')
print(papers_total, 'total papers')
print(pdf_total, 'were pdfs')
print(html_total, 'were webpages')
print(links_total, 'total links')
print('######## DATA PARSED INFO #######')
print(html_parsed, 'total html documents parsed')
print(html_errs, 'total html document unparsed')
print(pdf_parsed, 'total pdf documents parsed')
print(pdf_errs, 'total pdf documents unparsed')

print("######## ERRORS BY PROFESSOR #######")
print(prof_failures_dict)
