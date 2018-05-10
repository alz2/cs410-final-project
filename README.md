# cs410-final-project
We crawled over 12,000 research papers written by our UIUC Computer Science Faculty and provided a search interface for the papers.

## See it in action!
[Our app](https://whispering-reef-85517.herokuapp.com/)

Note that, on first visit, our app will take a while to load because it is deployed on Heroku.

## Crawler Installation (Uneeded for website, only for Crawler)

### On EWS
```
# install PhantomJS
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2
# ADD phantomjs-2.1.1-linux-x86_64.tar.bz2/bin to $PATH

# install scholarly
pip3 install scholarly --user

# install selenium
pip3 install selenium --user

# install PyPDF2
pip3 install pypdf2 --user
```

## Website Installation
```
# install Flask
pip3 install flask --user
# inside website/ directory
FLASK_APP=app.py flask app run
```

## Methodology For Retrieving Data for Inverted Index
1) Obtain list of names of all professors (see professors.txt)
2) For professors with google scholar profiles, e.g [Professor Zhai](https://scholar.google.com/citations?user=YU-baPIAAAAJ&hl=en&oi=ao) use Python module [scholarly](https://pypi.python.org/pypi/scholarly/0.2.3) obtain the links to papers.
3) For professors with no google scholar profiles find other way to obtain links -- maybe python module scholar to recursively crawl google scholar search results. (NOT YET IMPLMEENTED)
4) Save prof->links to papers dict to a json fill so previously crawled papers don't have to be crawled again.
5) For each link, take first n chars respecting word boundaries and also save into json


## Our Reasearch Paper Retriever (RPR) Crawler

#### Behavior
Our RPR is our crawler for obtaining the data we needed for buildling our inverted index. Given a list of names to crawl, the RPR crawler will utilize Google scholar profiles, like [this](https://scholar.google.com/citations?user=YU-baPIAAAAJ&hl=en&oi=ao) one to retrieve information on each paper on the profile. Specifically, the RPR crawler will retrieve

* The name of the research paper
* The link to the research paper
* Around 5000 characters, respecting word boundaries of the page/pdf behind the link.

#### Handling both PDFs and Web Documents
The RPR module handles both links that point to web documents as well as pdf files. If the link points to an html file, then the RPR module will attempt to eliniminate unhelpful html tags like script, and iframe. If the link points to a pdf file, then it will download the pdf into a temporary directory, scrape around 5000 characters, and then delete the file after saving the information it collected. 

#### Incremental Crawling
The RPR also supports incremental crawling via a history file. The history file is in the same format as the json file saved by the crawler. If there is sufficient information for each paper in the history file, the RPR crawler will not crawl it again. The history file is especially useful if the crawler runs into 503's in which it has to restart the crawl on a different IP. 

#### Example of using RPR Crawler Module To Crawl Papers Given List of Professors
```python
from crawl.rpr import PaperRetriever

# TEST 1 retreive papers for one professor with no history file
save_as_file = "test1.json" # the file which the data will be save to
profs = ['Svetlana Lazebnik', 'Chengxiang Zhai'] # crawl the papers of these professors
paper_retriever = PaperRetriever(profs, save_as_file, None, num_threads=3) # delegate the work on 3 threads without history
paper_retriever.retrieve()
```
