import json
import io

my_dict = {}

with io.open('test_json.json', 'r', encoding="utf-8") as json_file:
    my_dict = json.loads(json_file.read()) #read file into memory.


corpus_file = open("prof_data/prof_data.dat", "a", encoding="utf-8") #file to store individual documents. 
metadata_file = open("prof_data/metadata.dat", "a", encoding="utf-8") #file to store metadata about individual documents.




for curPerson in my_dict.keys():
    #for each professor

    i = 0
    
    for research_info in my_dict[curPerson]:
        #research_info is the  [doc title, doc link].  ***Also want some text of document (not currently available), so making up some text as  a temporary measure. 

        #create a new doc, using the author's name, document title and also some text from the document. 
        new_doc =  "{author} {title} {link}\n".format(author = curPerson, title = research_info[0], link = research_info[1])


        doc_content = "Text for doc number {} of Professor {} goes here".format(i, curPerson) #placeholder for actual document content

        
        new_doc_metadata = "{}	{}\n".format(research_info[1], doc_content)     #important: tab needed to delinate schema of each file for metadata.dat. 
        corpus_file.write(new_doc) #write as a document. one doc per line
        metadata_file.write(new_doc_metadata)

        i = i + 1 #increasing counter for documents. 



corpus_file.close()
metadata_file.close()
