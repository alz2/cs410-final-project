from paper_retriever import PaperRetriever

profs = ["Chengxiang Zhai", "Margaret Fleck"]
retriever = PaperRetriever(profs)
results = retriever.retrieve()
print(results)
