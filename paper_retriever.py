import scholarly
import json
from threading import Thread, Lock


seen_mutex = Lock()
results_mutex = Lock()
errors_mutex = Lock()

def _worker_paper_retrieve(author_publications, prof, results, errors, seen):
    for p in author_publications:
        if p.bib['title'] in seen: # seen this paper already
            continue
    
        pub_filled = p.fill() # get more information about publication
        # grab url if exists
        bib = pub_filled.bib

        # add unseen titles
        seen_mutex.acquire()
        try:
            seen.add(bib['title'])
        finally:
            seen_mutex.release()

        # add urls to dict
        results_mutex.acquire()
        try:
            if 'url' in bib:
                print(prof, bib['title'], bib['url'])
                results[prof].append( (bib['title'], bib['url']) )
            else:
                # log the title
                errors[prof].append(bib['title'])
        finally:
            results_mutex.release()


# https://stackoverflow.com/questions/2130016/splitting-a-list-into-n-parts-of-approximately-equal-length
def splitnchunks(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


class PaperRetriever:

    def __init__(self, professor_list, prior_file_name, num_threads=1):
        self.professors = professor_list # list of professor names
        self.results = {} # dict of key=professor, value=[(title, link),...] for each paper
        self.errors = {} # dict of key=professor, value=set of titles of papers in which errors were encounterd
        self.seen_papers = {} # dict of key=professor, value=set of titles of retrieved papers
        self.num_threads = num_threads

        if prior_file_name is not None: # open and read previously retrieved links
            prior_file = open(prior_file_name, "r");
            self.results = json.load(prior_file) # parse json
            # add to seen set to prevent re-retrieval
            for prof in self.results.keys():

                if prof not in seen_papers:
                    seen_papers[prof] = set()

                paper_tuples = self.results[prof]
                for paper in paper_tuples:
                    seen_papers[prof].add(paper[0]) # add the title to the corresponding set
            prior_file.close()


    def retrieve(self):
        for prof in self.professors:

            if prof not in self.results:
                self.results[prof] = []
                self.errors[prof] = []

            if prof not in self.seen_papers:
                self.seen_papers[prof] = set()

            # query scholar for author
            search_query = scholarly.search_author(prof) 
            try:
                author = next(search_query).fill()
            except StopIteration:
                # TODO HANDLE THIS CASE
                print(prof + " does not have a google scholar profile")
                continue

            # divide list of publications for threads
            author_publications = author.publications
            chunks = list(splitnchunks(author_publications, self.num_threads))

            # create and start threads
            t = []
            for i in range(self.num_threads):
                t.append(Thread(target=_worker_paper_retrieve, args=(chunks[i], prof, self.results, self.errors, self.seen_papers[prof])))
                t[i].start()

            # join threads
            for i in range(self.num_threads):
                t[i].join()
        
        return self.results

    def save_results_as_json(self, outfile_name):
        json_str = json.dumps(self.results)
        with open(outfile_name, "w+") as outfile:
            outfile_name.write(json_str)
        outfile.close()



