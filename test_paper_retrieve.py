from paper_retriever import PaperRetriever
from time import gmtime, strftime

history_file = "parsed_prof_papers.json"
save_as_file = "papers_" + strftime("%Y-%m-%d_%H:%M:%S", gmtime()) + ".json"

profs = ["Lui Sha", "Chengxiang Zhai", "Margaret Fleck"]
retriever = PaperRetriever(profs, save_as_file, history_file, num_threads=3) # num_threads=4 causes 503s :(
results = retriever.retrieve()
print(results)
