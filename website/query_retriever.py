#Script to get results for a given query.


import metapy
import sys

idx = metapy.index.make_inverted_index("config.toml")
ranker = metapy.index.OkapiBM25() #try different rankers to see which is best.



def get_matching_docs(txtToFind, numberOfResults = 10):
    print("Searching for:" + txtToFind)
    print()
    query = metapy.index.Document()
    query.content(txtToFind)
    best_docs = ranker.score(idx, query, num_results = numberOfResults)
    return best_docs


def print_results(best_docs):
    for num, (d_id, _) in enumerate(best_docs):
        #get title and content. 
        title = idx.metadata(d_id).get('title')
        content = idx.metadata(d_id).get('content')
        #print("{}. {}...\n".format(num + 1, content[0:30])) #number of characters in doc to print.
        result = "{resultNum}. {docTitle}\n{docTxt}\n".format(resultNum = num+1, docTitle = title, docTxt= content[0:50])
        print(result)





if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError('python3 query_retriever.py {QUERY}')
    best_docs = get_matching_docs(sys.argv[1]) #specify text to search for here
    print(best_docs)
    print_results(best_docs)






