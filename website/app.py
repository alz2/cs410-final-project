from flask import Flask, request, render_template
import metapy
import re


app = Flask(__name__)
idx = metapy.index.make_inverted_index("./config.toml")
ranker = metapy.index.OkapiBM25() #try different rankers to see which is best.

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_matching_docs(txtToFind, numberOfResults = 10):
    #print("Searching for:" + txtToFind)
    #print()
    query = metapy.index.Document()
    query.content(txtToFind)
    best_docs = ranker.score(idx, query, num_results = numberOfResults)
    return best_docs

def get_peripheral(text, target, n):
    corpus_words = text.split(" ")
    target_words = target.lower().split(" ")
    corpus_words_lower = text.lower().split(" ")
    attempt = 0
    found = False
    target_occur = -1
    while not found:
        try: # search lower case
            target_occur = corpus_words_lower.index(target_words[0], attempt)
        except ValueError:
            return ''
        # occurance of first string in target
        toff = 1
        found_seq = True
        for ti in range(1, len(target_words)):
            if target_words[toff] != corpus_words_lower[target_occur + ti]:
                found_seq = False
                break
            toff += 1

        if found_seq:
            found = True
        else:
            attempt = target_occur + 1 # try again at different location

    # sequence found! Try to take n chars left and right
    peripheral = corpus_words[max(0, target_occur - n) : min(target_occur + len(target_words) + n, len(corpus_words))]
    return ' '.join(peripheral)

def get_first_sentence(text):
    sentences = text.split('.')
    if len(sentences) < 2:
        return ''
    return sentences[0]

def format_results(best_docs, query):
    formatted = []
    for num, (d_id, _) in enumerate(best_docs):
        #get title and content. 
        title = idx.metadata(d_id).get('title')
        path = idx.metadata(d_id).get('path')
        content = cleanhtml(idx.metadata(d_id).get('content'))
        summary = get_peripheral(content, query, 10)
        if len(summary) == 0:
            summary = get_first_sentence(content)
        #print("{}. {}...\n".format(num + 1, content[0:30])) #number of characters in doc to print.
        result = "{resultNum}. <a href={url}>{docTitle}</a><p>...{desc}...</p>".format(resultNum = num+1, docTitle = title, url = path, desc = summary)
        formatted.append(result)
    return ("<p>" + "</p><p>".join(formatted) + "</p>") 


@app.route('/')
def hello():
    return render_template('main.html')

@app.route('/', methods=['POST'])
def my_form_post():
    query = request.form['text']
    print('querying', query)
    #processed_text = text.upper()
    best_docs = get_matching_docs(query) #specify text to search for here
    processed_text = format_results(best_docs, query)
    return processed_text



