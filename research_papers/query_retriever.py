#Script to get results for a given query.


import metapy

idx = metapy.index.make_inverted_index("config.toml")
ranker = metapy.index.OkapiBM25() #try different rankers to see which is best.



def get_matching_docs(txtToFind, numberOfResults = 10):
    query = metapy.index.Document()
    query.content(txtToFind)
    best_docs = ranker.score(idx, query, num_results = numberOfResults)
    return best_docs


def print_results(best_docs):
    for num, (d_id, _) in enumerate(best_docs):
        content = idx.metadata(d_id).get('content')
        print("{}. {}...\n".format(num + 1, content[0:30])) #number of characters in doc to print. 






best_docs = get_matching_docs("Zhai clustering") #specify text to search for here
print(best_docs)
print_results(best_docs)


