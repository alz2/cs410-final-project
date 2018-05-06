from crawl.rpr import PaperRetriever

# TEST 1 retreive papers for one professor with no history
save_as_file = 'test2.json'
profs = ['Svetlana Lazebnik']
history_file = 'test_history.json'
paper_retriever = PaperRetriever(profs, save_as_file, history_file, num_threads=3)
paper_retriever.retrieve()
