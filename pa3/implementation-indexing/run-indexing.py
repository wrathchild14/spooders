import sqlite3

from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize

import os

from stopwords import stop_words_slovene, stop_words_symbols

conn = sqlite3.connect('inverted-index.db')
c = conn.cursor()

# Index all HTML files in folder data
for root, dirs, files in os.walk('../data'):
    for file in files:
        if file.endswith(".html"):
            print("Indexing file " + file)
            with open(os.path.join(root, file), "r", encoding='utf8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Get whole textual data
                soup_text = soup.text
                # Tokenize
                tokens = word_tokenize(soup_text)
                # Normalization into lowercase letters
                tokens = [token.lower() for token in tokens]
                # Stopword removal
                filtered_tokens = [token for token in tokens if token not in stop_words_slovene and token not in stop_words_symbols]

                unique_tokens = []
                for token in filtered_tokens:
                    if token in unique_tokens:
                        continue
                    # Insert to table IndexWord
                    try:
                        c.execute("INSERT INTO IndexWord VALUES (?)", (token,))
                    except:
                        #print("Word " + token + " already exists in database.")
                        pass
                    # Insert to table Posting
                    indexes = []
                    for i in range(0, len(filtered_tokens)):
                        if token == filtered_tokens[i]:
                            indexes.append(str(i))
                    frequency = len(indexes)
                    document_name = root.replace("../data\\", "") + "/" + file
                    try:
                        c.execute("INSERT INTO Posting VALUES (?, ?, ?, ?)", (token, document_name, frequency, ",".join(indexes)))
                    except Exception as e:
                        print(e)
                    conn.commit()
                    unique_tokens.append(token)

conn.close()