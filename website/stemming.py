#Stemming functionality. Adapted from metapy tutorial. 
import metapy

def stem_string(original_str):
    """Return a list of words, where each word in original str has been stemmed"""
    doc = metapy.index.Document()
    doc.content(original_str)

    #make tokenizer and suppress tags to prevent boundary tags from being added.  (e.g. <s> and </s>)
    str_tokenizer = metapy.analyzers.ICUTokenizer(suppress_tags=True)
    str_tokenizer.set_content(doc.content())
    str_tokenizer = metapy.analyzers.Porter2Filter(str_tokenizer)
    str_tokenizer.set_content(doc.content())

    new_str = ""
    for token in str_tokenizer:
        new_str += token + " "

    return new_str






if __name__ == "__main__":
    print(stem_string("Happiness, food, eating, eat, test, testing, this is a simple test"))
    
    
    
    

    
