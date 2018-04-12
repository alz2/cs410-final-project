# cs410-final-project
Extending csillinois search feature

### Crawling Strategy
**Stage 0**: Creating professors.csv
  * For now: Manually lookup professors and record their CV's   
  * CV's tend to be in two formats -- html and pdf.
  * Prefer pdf over html!
  * CSV Schema: Professor_LN, Professor_FN, CV_Link, CV_CODE
      
**Stage 1**: Obtaining Links to Research Papers
  * Given: professors CSV in either html of pdf
  * In all cases try to retrieve links to research papers
  * In the case that links to a paper are not present in a cv (e.g [some of these](http://sifaka.cs.uiuc.edu/czhai/selected.html)) store the titles and other info into a list for later google processing
      
**Stage 2**: Adding disovered research papers to inverted index
  * Given: Link to reserach paper in PDF Format
  * Conduct inverted index calulation stuff (use metapy) and add to inverted index
      
**Stage 3**: Adding undiscovered research papers to inverted index
  * Given: Links to text information of undiscovered links from Stage 1.
  * Pass information to google scholar and then obtain links to pdf.
  * Go to Stage 2 to add these to inverted index
  
### Idea 2 for grabbing the Prof->links to papers
1) Obtain list of names of all professors
2) For professors with google scholar profiles, e.g [Professor Zhai](https://scholar.google.com/citations?user=YU-baPIAAAAJ&hl=en&oi=ao) use Python module [scholarly](https://pypi.python.org/pypi/scholarly/0.2.3) obtain the links to papers.
3) For professors with no google scholar profiles find other way to obtain links -- maybe python module scholar to recursively crawl google scholar search results.
4) Save prof->links to papers dict to a json fill so previously crawled papers don't have to be crawled again.
