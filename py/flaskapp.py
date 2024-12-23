from flask import Flask, request, render_template
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer
import os
import re

# dynamically determine the path to the templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))  # directory of flaskapp.py
template_dir = os.path.join(current_dir, "../templates")  # navigate to templates folder
static_dir = os.path.join(current_dir, "../static") # navigate to static folder

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Open the Whoosh index
search_index = open_dir("indexdir")

# Whoosh StemmingAnalyzer 
stem_ana = StemmingAnalyzer()

# home page
@app.route("/home/", methods=['GET'])
def home():
    # render a search fomr
    return render_template('home.html')

# fallback to home page
@app.route("/", methods=['GET'])
def home2():
    return render_template('home.html')

# search page to show results
@app.route("/search/", methods=['GET'])
def search():
    """
    Handling of search requests.

    - Retrieves search query from the request arguments
    - Uses Whoosh to process and execute search query
    - Highlights query words in the title, h1, and teaser

    Returns:
        - original query
        - search results to be rendered in the 'search.html' template
            consisting of url, title, keywords, description and teaser

    """
    # retrieve the search query
    query = request.args.get('q', '')
    results = []

    # perform the search
    if query:
        with search_index.searcher() as searcher:

            stemmed_query, parsed_query = process_query(query)
            whoosh_results = searcher.search(parsed_query)

            # Process each result only once
            for r in whoosh_results:
                url = r.get("url", "")
                title = r.get("title", "")
                h1_text = r.get("h1_text", "")
                keywords = r.get("keywords", "")
                description = r.get("description", "")
                content = r.get("content", "")

                # Extract the teaser
                teaser = extract_teaser(content, stemmed_query, h1_text, title)

                # highlight query in teaser and title (or h1 if existing)
                title, teaser = highlight_query_words(h1_text or title, teaser, query, stemmed_query)

                # Append result
                results.append({
                    "url": url,
                    "title": title,
                    "keywords": keywords,
                    "description": description,
                    "teaser": teaser,
                })

    return render_template('search.html', query=query, results=results)


def process_query(query):
    """
    Processes the search query by stemming and parsing it for Whoosh
    Param:
        query (str): The original search query entered by the user
    Returns:
        - stemmed_query (list): A list of stemmed words from the query
        - parsed_query (Query): A Whoosh query object ready for searching
    """

    print("original query: ", query)
    # Whoosh QueryParser
    qp = QueryParser("content", search_index.schema)

    # stemming with Whooosh StemmingAnalyzer
    stemmed_query = [word.text for word in stem_ana(query)]
    print("stemmed_query: ", stemmed_query)

    # parsing with QueryParser
    parsed_query = qp.parse(" ".join(stemmed_query))
    print("parsed query: ", parsed_query)

    return stemmed_query, parsed_query


def extract_teaser(content, stemmed_query, h1_text, title):
    """
    Extracts a teaser from the content based on the query words
    Param:
        content (str): The text content to search for teaser sentences
        stemmed_query (list): A list of stemmed query words
        h1_text (str): The H1 text of the document
        title (str): The title of the document
    Returns:
        str: A teaser string containing sentences with the query words or a fallback teaser

    """
    search_words = stemmed_query
    remaining_words = set(search_words)

    # Split the content into sentences with regex
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
    teaser = []

    # make sure that every query word appears in teaser
    while remaining_words:
        for word in list(remaining_words):
            # Find the sentence that contains the query word
            for sentence in sentences:
                if word in sentence.lower():  # Case-insensitive match for query
                    teaser.append(sentence.strip())
                    # remove words that are covered in teaser so far
                    remaining_words -= set(w for w in search_words if w in sentence.lower())
                    break
            break

        # if all query words are covered
        if not remaining_words:
            break

    if teaser:
        # Join collected sentences with " ... "
        teaser_complete = " ... ".join(teaser).strip()
    else:
        teaser_complete = content[:200].strip()  # Return the first 200 characters of the content as fallback teaser
    # cut title from teaser
    if h1_text:
        teaser_complete = teaser_complete.replace(h1_text, "").replace(title, "").strip()
    else:
        teaser_complete = teaser_complete.replace(title, "").strip()
    return teaser_complete + " ... "


def highlight_query_words(title, teaser, original_query, stemmed_query):
    """
    Highlight the query word(s) in the title or h1 and teaser by wrapping them in a span tag 
    with the class 'highlight'. Original query words are prioritized for exact matches.
    Stemmed query highlights handle partial matches when the exact word is not found.
    Regular expressions are used for precise word boundary detection and flexibility.

    Param:
        title (str): The title or H1 text to highlight
        teaser (str): The teaser text to highlight
        original_query (str): The original search query entered by the user
        stemmed_query (list): A list of stemmed query words
    
    Returns:
        tuple: containing the updated title and teaser with highlights

    """
    original_query = original_query.split()

    for original_word, stemmed_word in zip(original_query, stemmed_query):

        # Teaser: Match the original word as a full word
        teaser = re.sub(rf"(\b{re.escape(original_word)}\b)", r'<span class="highlight">\1</span>', teaser, flags=re.IGNORECASE)
        # Teaser: Match any word containing the stemmed word
        teaser = re.sub(rf"(\b\w*{re.escape(stemmed_word)}\w*\b)", r'<span class="highlight">\1</span>', teaser, flags=re.IGNORECASE)

        # Title: Match the original word as a full word
        title = re.sub(rf"(\b{re.escape(original_word)}\b)", r'<span class="highlight">\1</span>', title, flags=re.IGNORECASE)
        # Title: Match any word containing the stemmed word
        title = re.sub(rf"(\b\w*{re.escape(stemmed_word)}\w*\b)", r'<span class="highlight">\1</span>', title, flags=re.IGNORECASE)

    return title, teaser


@app.errorhandler(404)
def page_not_found(error):
    return render_template('not-found.html'), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)  # port5500 as default