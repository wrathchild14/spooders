import sqlite3

from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize

import sys, time, os

from stopwords import stop_words_slovene, stop_words_symbols

def form_snippet(document_path, indexes):
    indexes = [int(i) for i in indexes.split(",")]
    if len(indexes) > 5: # Limit snippet output to 5 indexes
        indexes = indexes[:5]

    snippet = ""
    with open(os.path.join("../data",document_path), "r", encoding='utf8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        soup_text = soup.text
        tokens = word_tokenize(soup_text)
        tokens = [token.lower() for token in tokens]
        tokens = [token for token in tokens if token not in stop_words_slovene and token not in stop_words_symbols]
        
        for index in indexes:
            if index-2 > 0:
                snippet += "..."
                if (len(snippet)>=6 and snippet[len(snippet)-6] != "......"):
                    snippet = snippet[:len(snippet)-3]
            snippet += tokens[index-2] + " " + tokens[index-1] + " " + tokens[index]
            if index+2 < len(tokens):
                snippet += " " + tokens[index+1] + " " + tokens[index+2]
            if index+3 < len(tokens):
                snippet += "..."

    return snippet

# Run search only if query provided
# Get query string from command line arguments
if len(sys.argv) == 2:
    query = sys.argv[1]
    print('Results for a query: "' + query + '"\n')

    # Prereprocess query
    tokens = word_tokenize(query)
    tokens = [token.lower() for token in tokens if token not in stop_words_slovene and token not in stop_words_symbols]
    tokens = " ".join(tokens)
    query_tokens = ",".join(map(lambda x: "'" + x + "'", tokens.split(' ')))
    #print(query_tokens)

    # Retrieve data
    conn = sqlite3.connect('inverted-index.db')
    start_time = time.time()
    c = conn.cursor()

    # Get all documents that contain query words
    sql_query = "SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs FROM Posting p WHERE p.word IN (" + query_tokens + ") GROUP BY p.documentName ORDER BY freq DESC"
    cursor = c.execute(sql_query)
    
    print("Results found in " + str((time.time()-start_time)*1000) + "ms.\n")
    print("{: <15} {: <45} {: <0}".format("Frequencies","Document","Snippet"))
    print("{: <15} {: <45} {: <0}".format("-----------","-----------------------------------------","-----------------------------------------"))
    for row in cursor:
        snippet = form_snippet(row[0], row[2])
        print("{: <15} {: <45} {: <0}".format(row[1],row[0],snippet))
        print()

    conn.close()