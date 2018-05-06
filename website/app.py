from flask import Flask, request, render_template
import metapy


app = Flask(__name__)
idx = metapy.index.make_inverted_index("./config.toml")
ranker = metapy.index.OkapiBM25() #try different rankers to see which is best.



def get_matching_docs(txtToFind, numberOfResults = 10):
    #print("Searching for:" + txtToFind)
    #print()
    query = metapy.index.Document()
    query.content(txtToFind)
    print('query doc created')
    print(ranker)
    best_docs = ranker.score(idx, query, num_results = numberOfResults)
    return best_docs


def format_results(best_docs):
    formatted = []
    for num, (d_id, _) in enumerate(best_docs):
        #get title and content. 
        title = idx.metadata(d_id).get('title')
        content = idx.metadata(d_id).get('content')
        #print("{}. {}...\n".format(num + 1, content[0:30])) #number of characters in doc to print.
        result = "{resultNum}. {docTitle}\n{docTxt}\n".format(resultNum = num+1, docTitle = title, docTxt= content[0:50].replace('<', '').replace('>', ''))
        formatted.append(result)
        print(result)
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
    print('found best docs')
    processed_text = format_results(best_docs)
    return processed_text



