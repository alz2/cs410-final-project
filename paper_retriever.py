import scholarly
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
                results[prof].append(bib['url'])
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
    def __init__(self, professor_list, num_threads=1):
        self.professors = professor_list
        self.results = {}
        self.errors = {}
        self.num_threads = num_threads;

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
                print(prof + " does not have a google scholar profile")
                continue

            # divide list
            author_publications = author.publications
            chunks = list(splitnchunks(author_publications, self.num_threads))

            # create and start threads
            t = []
            for i in range(self.num_threads):
                t.append(Thread(target=_worker_paper_retrieve, args=(chunks[i], prof, self.results, self.errors, seen_titles)))
                t[i].start()

            # join threads
            for i in range(self.num_threads):
                t[i].join()
        
        return self.results


