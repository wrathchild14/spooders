import sqlite3

def drop_tables(c): #cursor c
    c.execute('DROP TABLE IF EXISTS IndexWord')
    c.execute('DROP TABLE IF EXISTS Posting')

def create_tables(c):
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

# Create database file if does not exist and connect to it
conn = sqlite3.connect('inverted-index.db')

# Create table
c = conn.cursor()

create_tables(c)
#drop_tables(c)

# Save (commit) the changes
conn.commit()

# Close the connection if we are done with it
conn.close()