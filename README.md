# cs410-final-project
Extending csillinois search feature

### Crawling Strategy
  0) **Stage 0**: Creating professors.csv
      - For now: Manually lookup professors and record their CV's
      - CV's tend to be in two formats -- html and pdf.
  1) **Stage 1**: Obtaining Links to Research Papers
      - Given: professors.csv
      - Case 1: pdf
      - Case 2: html
      - Case 3: txt
      - In all cases try to retrieve links to research papers
      - In the case that links to a paper are not present in a cv (e.g [some of these](http://sifaka.cs.uiuc.edu/czhai/selected.html)) store the titles and other info into a list for later google processing
  2) **Stage 2**: Adding disovered research papers to inverted index
      - Given: Link to reserach paper in PDF Format
      - Conduct inverted index calulation stuff (use metapy) and add to inverted index
  3) **Stage 3**: Adding undiscovered research papers to inverted index
      - Given: Links to text information of undiscovered links from Stage 1.
      - Pass information to google scholar and then obtain links to pdf.
      - Go to Stage 2 to add these to inverted index
