from crawl.rpr import PaperRetriever

# TEST 1 retreive papers for one professor with no history
save_as_file = "test1.json"
profs = ['Svetlana Lazebnik']
paper_retriever = PaperRetriever(profs, save_as_file, None, num_threads=3)
paper_retriever.retrieve()
