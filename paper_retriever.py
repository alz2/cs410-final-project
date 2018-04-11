import scholarly

class PaperRetriever:
    def __init__(self, professor_list):
        self.professors = professor_list
        self.results = {}
        self.errors = {}

    def retrieve(self):
        for prof in self.professors:

            self.results[prof] = []
            self.errors[prof] = []

            seen_titles = set() # keep track of seen tites

            search_query = scholarly.search_author(prof) 
            try:
                author = next(search_query).fill()
            except StopIteration:
                # TODO HANDLE THIS CASE
                print(prof + "Does not have a google scholar profile")
                continue

            for p in author.publications:
                if (p.bib['title'] in seen_titles): # seen this paper already
                    continue
            
                pub_filled = p.fill() # get more information about publication
                # grab url if exists
                bib = pub_filled.bib
                seen_titles.add(bib['title'])
                if 'url' in bib:
                    print(prof, bib['title'], bib['url'])
                    self.results[prof].append(bib['url'])
                else:
                    # log the title
                    self.errors[prof].append(bib['title'])
        
        return self.results

