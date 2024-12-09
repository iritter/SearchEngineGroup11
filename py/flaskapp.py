from flask import Flask, request, render_template

app = Flask(__name__)

# exemplatory search index
search_index = {
    "python": ["https://www.python.org/", "https://docs.python.org/3/"],
    "flask": ["https://flask.palletsprojects.com/", "https://realpython.com/tutorials/flask/"],
    "web development": ["https://developer.mozilla.org/en-US/docs/Learn", "https://www.w3schools.com/"]
}

# start page
@app.route("/")
def start():
    return render_template('start.html')

# reverse the inputted(?) word
@app.route("/reversed")
def reversed():
    rev = request.args['rev'][::-1]
    return render_template('reversed.html', rev=rev)

@app.route("/home", methods=['GET'])
def home():
    # render a search fomr
    return render_template('home.html')

@app.route("/search", methods=['GET'])
def search():
    # retrieve the search query
    query = request.args.get('q', '').lower()
    # perform the search
    results = search_index.get(query, [])
    return render_template('search.html', query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)  # port 5500
