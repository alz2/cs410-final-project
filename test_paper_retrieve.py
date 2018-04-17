from paper_retriever import PaperRetriever

profs = ["Lui Sha", "Margaret Fleck"]
retriever = PaperRetriever(profs, "parsed_prof_papers.json", None, num_threads=3) # num_threads=4 causes 503s :(
results = retriever.retrieve()
print(results)
