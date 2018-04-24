from paper_retriever import PaperRetriever
from time import gmtime, strftime

history_file = "parsed_prof_papers.json"
save_as_file = "papers_" + strftime("%Y-%m-%d_%H:%M:%S", gmtime()) + ".json"


profs = []
profs_file = 'professors.txt'
with open(profs_file, 'r') as pfile:
    for p in pfile:
        if (p[-1] == '\n'): # don't keep the new line!
            profs.append(p[len(p) - 1])
        else:
            profs.append(p)

retriever = PaperRetriever(profs, save_as_file, history_file, num_threads=3) # num_threads=4 causes 503s :(
results = retriever.retrieve()
print(results)
