from flask import Flask, request, render_template
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
from urllib.parse import urlparse

# dynamically determine the path to the templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))  # directory of flaspapp.py
template_dir = os.path.join(current_dir, "../templates")  #navigate to templates folder
static_dir = os.path.join(current_dir, "../static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Open the Whoosh index
search_index = open_dir("indexdir")

# home page
@app.route("/")
def home1():
    return render_template('home.html')

# reverse the inputted(?) word
# @app.route("/reversed")
# def reversed():
#     rev = request.args['rev'][::-1]
#     return render_template('reversed.html', rev=rev)

# home page
@app.route("/home", methods=['GET'])
def home2():
    # render a search fomr
    return render_template('home.html')

@app.route("/search", methods=['GET'])
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
            qp = QueryParser("content", search_index.schema)  # Assuming "content" is the field you want to search
            parsed_query = qp.parse(query)
            whoosh_results = searcher.search(parsed_query)

            # Collect the URLs 
            for r in whoosh_results:
                url = r["url"]
                title = r["title"]
                teaser = r["content"]
                results.append({"url": url, "title": title, "teaser": teaser})
                
    return render_template('search.html', query=query, results=results)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('not-found.html'), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)  # port5500








