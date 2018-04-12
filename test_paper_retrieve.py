from paper_retriever import PaperRetriever

profs = ["Chengxiang Zhai", "Margaret Fleck"]
retriever = PaperRetriever(profs, num_threads=3)
results = retriever.retrieve()
print(results)
