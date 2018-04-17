import scholarly
import json
from threading import Thread, Lock


seen_mutex = Lock()
results_mutex = Lock()
errors_mutex = Lock()

papers_retrieved_per_professor = 0

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
                results[prof].append( (bib['title'], bib['url']) )
                papers_retrieved_per_professor += 1
                print(prof + ": " + str(papers_retrieved_per_professor)) # log to console
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

    """
        Constructor for the PaperRetriever:
        Params:
            professor_list: List of professor names
            history: a json dict of previously retrived dict of key=professor, value=[(title, link)]. 
                    Can be None if running without history
            num_threads: (default 1) Number of threads used to parse scholar... be careful of 503s
            save_as: file to the newly parsed json
            
    """
    def __init__(self, professor_list, save_as, history, num_threads=1):
        if professor_list is None:
            raise ValueError('Must provide a list of professors')

        self.professors = professor_list # list of professor names
        self.results = {} # dict of key=professor, value=[(title, link),...] for each paper
        self.seen_papers = {} # dict of key=professor, value=set of titles of retrieved papers
        self.errors = {}
        if save_as is None:
            raise ValueError('Must provide a save file')
        self.save_as = save_as
        self.num_threads = num_threads

        # open and read previously retrieved links
        if history is not None:
            prior_file = open(history, "r");
            self.results = json.load(prior_file) # parse json
            # add to seen set to prevent re-retrieval
            for prof in self.results.keys():

                if prof not in seen_papers:
                    self.seen_papers[prof] = set()

                paper_tuples = self.results[prof]
                for paper in paper_tuples:
                    seen_papers[prof].add(paper[0]) # add the title to the corresponding set
            prior_file.close()


    def retrieve(self):
        for prof in self.professors:

            print("Retrieving Papers for ", prof)
            papers_retrieved_per_professor = 0

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

            # save the file
            self.save_results_as_json()
            self.save_errors_as_json()
        
        return self.results


    def save_results_as_json(self):
        json_str = json.dumps(self.results)
        with open(self.save_as, "w+") as outfile: # truncate aka rewrite
            outfile.write(json_str)
        outfile.close()

    def save_errors_as_json(self):
        json_str = json.dumps(self.errors)
        if len(json_str) != 0:
            err_file_name = "ERRORS_" + self.save_as 
            with open(err_file_name, "w+"):
                err_file_name.write(json_str)
            err_file_name.close()



