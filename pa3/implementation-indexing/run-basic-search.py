from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize

import sys, time, os

from stopwords import stop_words_slovene, stop_words_symbols

def form_snippet(text_tokens, document_path, indexes): # Already provided preprocessed text in text_tokens
    if len(indexes) > 5: # Limit snippet output to 5 indexes
        indexes = indexes[:5]

    snippet = ""
    for index in indexes:
        if index-2 > 0:
            snippet += "..."
            if (len(snippet)>=6 and snippet[len(snippet)-6] != "......"):
                snippet = snippet[:len(snippet)-3]
        snippet += text_tokens[index-2] + " " + text_tokens[index-1] + " " + text_tokens[index]
        if index+2 < len(text_tokens):
            snippet += " " + text_tokens[index+1] + " " + text_tokens[index+2]
        if index+3 < len(text_tokens):
            snippet += "..."

    return snippet

# Run search only if query provided
# Get query string from command line arguments
if len(sys.argv) == 2:
    query = sys.argv[1]
    print('Results for a query: "' + query + '"\n')

    # Prereprocess query
    query = word_tokenize(query)
    query = [token.lower() for token in query if token not in stop_words_slovene and token not in stop_words_symbols]

    # Retrieve data without SQLite database
    start_time = time.time()

    rows = [] # Save frequency, document_name and snippet for query words (tokens )
    # Go through all HTML files in folder data
    for root, dirs, files in os.walk('../data'):
        for file in files:
            if file.endswith(".html"):
                with open(os.path.join(root, file), "r", encoding='utf8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    soup_text = soup.text
                    tokens = word_tokenize(soup_text)
                    tokens = [token.lower() for token in tokens]
                    filtered_tokens = [token for token in tokens if token not in stop_words_slovene and token not in stop_words_symbols and any(c.isalpha() for c in token)]
                    # Find tokens from query in document and save document_name, frequency and snippet
                    for query_token in query:
                        if query_token in filtered_tokens:
                            document_name = root.replace("../data\\", "") + "/" + file
                            indexes = []
                            for i in range(0, len(filtered_tokens)):
                                if query_token == filtered_tokens[i]:
                                    indexes.append(i)
                            frequency = len(indexes)
                            snippet = form_snippet(filtered_tokens, document_name, indexes)
                            rows.append([document_name, frequency, snippet])

    # Sort rows by frequency descending
    rows.sort(key=lambda x: x[1], reverse=True)

    print("Results found in " + str(time.time()-start_time) + "s.\n")
    print("{: <15} {: <45} {: <0}".format("Frequencies","Document","Snippet"))
    print("{: <15} {: <45} {: <0}".format("-----------","-----------------------------------------","-----------------------------------------"))
    for row in rows:
        print("{: <15} {: <45} {: <0}".format(row[1],row[0],row[2]))
        print()