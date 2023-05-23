import sqlite3

# Create database file if does not exist and connect to it
conn = sqlite3.connect('inverted-index.db')

# Create table
c = conn.cursor()

c.execute('''
    CREATE TABLE IndexWord (
        word TEXT PRIMARY KEY
    );
''')

c.execute('''
    CREATE TABLE Posting (
        word TEXT NOT NULL,
        documentName TEXT NOT NULL,
        frequency INTEGER NOT NULL,
        indexes TEXT NOT NULL,
        PRIMARY KEY(word, documentName),
        FOREIGN KEY (word) REFERENCES IndexWord(word)
    );
''')

# Save (commit) the changes
conn.commit()

# Close the connection if we are done with it
conn.close()