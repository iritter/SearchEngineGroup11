from whoosh.index import create_in
from whoosh.fields import Schema, TEXT

#added following: 
# Define the schema for the index
# The schema specifies the fields you will store and search 
schema = Schema(title=TEXT(stored=True), content=TEXT)

# Create an index in the "indexdir" directory (the directory must already exist!)
import os
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

# Create the index
ix = create_in("indexdir", schema)
writer = ix.writer()

# Add some documents to the index
writer.add_document(title=u"First document", content=u"This is the first document we've added!")
writer.add_document(title=u"Second document", content=u"The second one is even more interesting!")
writer.add_document(title=u"Songtext", content=u"Music was my first love and it will be the last")

# Write the index to the disk
writer.commit()

# Retrieving data
from whoosh.qparser import QueryParser

# Perform a search
with ix.searcher() as searcher:
    # Search for entries containing the words 'first' AND 'last'
    query = QueryParser("content", ix.schema).parse("first last")
    results = searcher.search(query)

    # Print all results
    for r in results:
        print(r)
