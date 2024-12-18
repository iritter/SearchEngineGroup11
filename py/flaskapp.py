from flask import Flask, request, render_template
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
from bs4 import BeautifulSoup
import requests

# dynamically determine the path to the templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))  # directory of flaspapp.py
template_dir = os.path.join(current_dir, "../templates")  #navigate to templates folder
static_dir = os.path.join(current_dir, "../static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Open the Whoosh index
search_index = open_dir("indexdir")

# home page
@app.route("/home/", methods=['GET'])
def home2():
    # render a search fomr
    return render_template('home.html')
import re

@app.route("/search/", methods=['GET'])
def search():
    """
    Perform a search query using Whoosh index.
    """
    # retrieve the search query
    query = request.args.get('q', '').lower()
    results = []

    # perform the search
    if query:
        with search_index.searcher() as searcher:
            qp = QueryParser("content", search_index.schema)
            parsed_query = qp.parse(query)
            whoosh_results = searcher.search(parsed_query)

            # Process each result only once
            for r in whoosh_results:
                url = r["url"]
                title = r["title"]
                keywords = r.get("keywords", "No keywords")
                description = r.get("description", "No description available")
                content = r["content"]

                # Try to fetch the page and extract <h1> from the body
                try:
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Find the <body> tag
                    body = soup.find('body')
                    h1 = body.find('h1') if body else None
                    h1_text = h1.get_text() if h1 else None

                except Exception as e:
                    print(f"Error fetching {url}: {e}")
                    h1_text = None

                # Extract the teaser and highlight query words
                teaser = extract_teaser(content, query)
                teaser = highlight_query_in_teaser(teaser, query)

                # Exclude title or h1 from teaser if present
                if h1_text:
                    teaser = teaser.replace(h1_text, "").replace(title, "").strip()
                else:
                    teaser = teaser.replace(title, "").strip()

                # Append result
                results.append({
                    "url": url,
                    "title": h1_text or title,
                    "keywords": keywords,
                    "description": description,
                    "teaser": teaser,
                })

    return render_template('search.html', query=query, results=results)


def extract_teaser(content, query):
    """
    Extract a sentence that contains the query word(s) to form a teaser.
    """
    # Split the content into sentences (you can use regex or any other sentence split method)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)

    # Find the sentence that contains the query word(s)
    for sentence in sentences:
        if query in sentence.lower():  # Case-insensitive match for query
            # Clean up extra spaces and return the sentence with the query
            return sentence.strip()

    # If no matching sentence is found, return a default teaser or empty string
    return content[:200].strip()  # Return the first 200 characters of the content as fallback teaser

def highlight_query_in_teaser(teaser, query):
    """
    Highlight the query word(s) in the teaser by wrapping them in a span tag with the class 'highlight'.
    """
    query_words = query.split()  # Split the query into individual words
    for word in query_words:
        # Use a case-insensitive replace to highlight all occurrences of the query words
        teaser = re.sub(r'(' + re.escape(word) + r')', r'<span class="highlight">\1</span>', teaser, flags=re.IGNORECASE)
    return teaser


@app.errorhandler(404)
def page_not_found(error):
    return render_template('not-found.html'), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)  # port5500