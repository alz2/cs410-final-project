from flask import Flask, request, render_template
import metapy
import re
from jinja2 import Markup


app = Flask(__name__)
idx = metapy.index.make_inverted_index("./config.toml")
ranker = metapy.index.OkapiBM25() #try different rankers to see which is best.
RESULTS_PER_PAGE = 10


def stem_string(original_str):
    """Return a list of words, where each word in original str has been stemmed"""
    doc = metapy.index.Document()
    doc.content(original_str)

    #make tokenizer and suppress tags to prevent boundary tags from being added.  (e.g. <s> and </s>)
    str_tokenizer = metapy.analyzers.ICUTokenizer(suppress_tags=True)
    str_tokenizer.set_content(doc.content())
    str_tokenizer = metapy.analyzers.Porter2Filter(str_tokenizer)
    str_tokenizer.set_content(doc.content())

    new_str = ""
    for token in str_tokenizer:
        new_str += token + " "

    return new_str


"""
    Polls inverted index given a page number and number of results per page
"""
def get_matching_docs(txtToFind, page_no, numberOfResults = RESULTS_PER_PAGE):
    #print("Searching for:" + txtToFind)
    #print()
    query = metapy.index.Document()
    query.content(txtToFind)
    total_results_needed = page_no * numberOfResults
    best_docs = ranker.score(idx, query, num_results = total_results_needed)
    return best_docs[(page_no - 1) * numberOfResults : page_no * numberOfResults]


"""
    Returns indices of n words around <target> in corpus <text>. If there are multiple occurances
    of <target> the function will only act on the first occurance. 

    The function will look for the target words next to eachother. Otherwise it will default searching
    singular words in the target words.

    Returns (-1, -1) if target words are not found.
"""
def get_peripheral(corpus_words, target_words, n):
    corpus_words_lower = [t.lower() for t in corpus_words]
    attempt = 0 # index to begin search
    found = False
    target_occur = -1
    while not found:
        try: # search lower case
            target_occur = corpus_words_lower.index(target_words[0], attempt)
        except ValueError:
            return (-1, -1)
        # occurance of first string in target
        toff = 1
        found_seq = True
        for ti in range(1, len(target_words)): # search next words to see if they match query
            if target_occur + ti >= len(corpus_words_lower): # no more words in corpus
                return (-1 , -1)

            if target_words[toff] != corpus_words_lower[target_occur + ti]:
                found_seq = False
                break
            toff += 1

        if found_seq:
            found = True
        else:
            attempt = target_occur + 1 # try again at different location

    # sequence found! Try to get indices for n words left and right
    return (max(0, target_occur - n), min(target_occur + len(target_words) + n, len(corpus_words)))


def add_emphasis(corpus, target):
    lower_target = stem_string(target.lower())
    corpus_words = corpus.split(" ")
    for cwi in range(len(corpus_words)):
        if stem_string(corpus_words[cwi]).lower() == lower_target:
            corpus_words[cwi] = '<strong>' + corpus_words[cwi] + '</strong>'
    return ' '.join(corpus_words)

"""
    Returns first sentence of text.
"""
def get_first_sentence(text):
    sentences = text.split('.')
    if len(sentences) < 2:
        return ''
    return sentences[0]


"""
    Formats results returned by metapy in a format expected by the template results.html
"""
def format_results(best_docs, query): 
    # stem the queryquery 
    stemmed_query_wds = stem_string(query).split(" ")
    if stemmed_query_wds[-1] == "": # weird split case
        del stemmed_query_wds[-1]

    # result (link, title, description)
    formatted = []
    for num, (d_id, _) in enumerate(best_docs):
        search_result = [] 
        path = idx.metadata(d_id).get('path') # get the link
        search_result.append(path)

        title = idx.metadata(d_id).get('title') # get the title
        search_result.append(title)
        
        # figure out the description
        content_corp = idx.metadata(d_id).get('content') # get the raw content
        c_doc = metapy.index.Document()
        c_doc.content(content_corp)
        c_tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
        c_tok.set_content(c_doc.content())
        content_wds = [t for t in c_tok]
        
        # stemmed content
        stemmed_corp = idx.metadata(d_id).get('stemmedcontent')
        sc_doc = metapy.index.Document()
        sc_doc.content(stemmed_corp)
        sc_tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
        sc_tok.set_content(sc_doc.content())
        stemmed_content_wds = [t for t in sc_tok]
        si = get_peripheral(stemmed_content_wds, stemmed_query_wds, 15)

        if si[0] == -1: # none found for all
            for sq in stemmed_query_wds: # try for each word
                si = get_peripheral(stemmed_content_wds, [sq], 15)
                if si[0] != -1: # found valid peripheral
                    print('found', sq, 'at', si)
                    break

            if si[0] == -1:
                summary = 'Sorry, No Description Available.'
            else:
                query_words = query.split(" ")
                summary = ' '.join(content_wds[si[0]: si[1]])
                summary += '...'
                # add emphasis to the query words
                for q in query_words:
                    summary = add_emphasis(summary, q)
                summary = Markup(summary) # preserve markup tags
        else: # found both terms next to each other
            query_words = query.split(" ")
            summary = ' '.join(content_wds[si[0]: si[1]])
            summary += '...'
            for q in query_words:
                summary = add_emphasis(summary, q)
            summary = Markup(summary) # preserve markup tags

        search_result.append(summary)
        formatted.append(search_result)
     
    return formatted


@app.route('/')
def hello():
    return render_template('main.html')

"""
    Search endpoint
"""
@app.route('/', methods=['POST'])
def my_form_post():
    query = request.form['query'].lower()
    if len(query) == 0:
        return render_template('main.html')
    try:
        page_no = int(request.form['page_no'])
    except: # from the home page
        page_no = 1

    print('querying', query)

    best_docs = get_matching_docs(query, page_no) #specify text to search for here
    search_results = format_results(best_docs, query)
    return render_template('results.html', search_results=search_results, num_results=len(best_docs), query=query, page_no=page_no)



