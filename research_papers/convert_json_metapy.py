import json
import io

my_dict = {}

with io.open('../data/papers_2018-05-03_01-58-24.json', 'r', encoding="utf-8") as json_file:
    my_dict = json.loads(json_file.read()) #read file into memory.


corpus_file = open("prof_data/prof_data.dat", "a", encoding="utf-8") #file to store individual documents. 
metadata_file = open("prof_data/metadata.dat", "a", encoding="utf-8") #file to store metadata about individual documents.




for curPerson in my_dict.keys():
    #for each professor

    i = 0


    if len(my_dict[curPerson]) == 0: #if there is no data for a given professor, move on. 
            continue #no data. 

    for research_info in my_dict[curPerson]:
        #research_info is the  [doc title, doc link, doc text] for one professor.

      
        #create a new doc, using the author's name, document title and also some text from the document.
        docText = research_info[2]
        if not docText.strip():
            docText = "Text not available for this document"


        
        new_doc =  "{author} {title} {docTxt}\n".format(author = curPerson, title = research_info[0], docTxt = docText)


       # doc_content = "Text for doc number {} of Professor {} goes here".format(i, curPerson) #placeholder for actual document content

        
        new_doc_metadata = "{}	{}	{}\n".format(research_info[0], research_info[1], docText[:500])     #important: tab needed to delinate schema of each file for metadata.dat.
                                                                                            #only store the first 1000 characters of data in the metadata file. 
        corpus_file.write(new_doc) #write as a document. one doc per line
        metadata_file.write(new_doc_metadata)

        i = i + 1 #increasing counter for documents. 



corpus_file.close()
metadata_file.close()
