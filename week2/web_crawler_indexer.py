from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# Initialize stemmer and lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the schema for the index
schema = Schema(url=ID(stored=True, unique=True), title=TEXT(stored=True), content=TEXT(stored=True))

# Create an index directory if it doesn't exist
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

# Create the Whoosh index
ix = create_in("indexdir", schema)

def add_to_index(writer, url, title, content):
    """
    Add a document to the Whoosh index.
    """
    writer.add_document(url=url, title=title, content=content)


def process_search_query(query_words, use_stemming=False, use_lemmatization=False):
    """
    Process the search query by applying stemming or lemmatization.
    """
    processed_words = []
    for word in query_words:
        if use_stemming:
            processed_words.append(stemmer.stem(word))
        elif use_lemmatization:
            processed_words.append(lemmatizer.lemmatize(word))
        else:
            processed_words.append(word)
    return processed_words


def crawl_and_index(initial_url):
    """
    Crawl a website starting from the initial URL and index its pages using Whoosh.
    """
    visited = set()
    agenda = [initial_url]
    base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(initial_url))

    with ix.writer() as writer:
        while agenda:
            url = agenda.pop()  # Get the next URL to crawl
            if url in visited:
                continue

            visited.add(url)
            try:
                # Fetch the page
                response = requests.get(url)
                if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string if soup.title else "No title"
                    content = soup.get_text(separator=" ").strip()

                    # Index the page
                    add_to_index(writer, url=url, title=title, content=content)

                    # Extract and queue all links
                    for link in soup.find_all('a', href=True):
                        absolute_url = urljoin(url, link['href'])
                        if absolute_url.startswith(base_url) and absolute_url not in visited:
                            agenda.append(absolute_url)

            except requests.RequestException as e:
                logging.error(f"Failed to fetch {url}: {e}")

def search_index(query, use_stemming=False, use_lemmatization=False):
    """
    Search the Whoosh index for the given query.
    """
    # Process the query words
    query_words = query.split()  # Split the query into individual words
    processed_query_words = process_search_query(query_words, use_stemming, use_lemmatization)
    query_str = " ".join(processed_query_words)  # Reconstruct the query string
    
    logging.info(f"Processed query string: {query_str}")
    
    with ix.searcher() as searcher:
        # Parse and execute the query
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query)

        # Return the results as a list of tuples (URL, Title)
        return [(r['title'], r.highlights('content')) for r in results]

# Main function to run crawling and searching
if __name__ == "__main__":
    # Define the initial URL to crawl
    initial_url = 'https://vm009.rz.uos.de/crawl/index.html'

    # Start crawling and indexing
    logging.info("Crawling and indexing...")
    crawl_and_index(initial_url)
    logging.info("Crawling and indexing completed.")

    # Perform a search with stemming or lemmatization
    search_query = ['symbol', 'virgins', 'graced']
    use_stemming = True  # Set to True for stemming
    use_lemmatization = False  # Set to True for lemmatization
    
    processed_query = process_search_query(search_query, use_stemming, use_lemmatization)
    search_query_str = " ".join(processed_query)
    logging.info(f"Searching for query: {search_query_str}")
    search_results = search_index(search_query_str)

    # Display the results
    if search_results:
        logging.info(f"Found {len(search_results)} results:")
        for url, title in search_results:
            print(f"Title: {url}, Highlight: {title}")
    else:
        logging.info("No results found.")
