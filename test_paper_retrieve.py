from paper_retriever import PaperRetriever

profs = ["Lui Sha", "Margaret Fleck"]
retriever = PaperRetriever(profs, None, num_threads=3) # num_threads=4 causes 503s :(
results = retriever.retrieve()
retriever.save_results_as_json("parsed_professor_papers.json")
print(results)
