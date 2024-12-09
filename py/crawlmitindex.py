from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import re
from collections import defaultdict


# Define the schema for the index
# The schema specifies the fields you will store and search 
schema = Schema(url=ID(stored=True), title=TEXT(stored=True), content=TEXT)

# Create an index in the "indexdir" directory (the directory must already exist!)
import os
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

# Create the index
ix = create_in("indexdir", schema)
writer = ix.writer()

# Write the index to the disk
writer.commit()

def add_to_index(writer, url, title, content):
    """
    Add a document to the Whoosh index.
    """
    writer.add_document(url=url, title=title, content=content)


# perform a search
def perform_search(q_words):
    """
    Perform a search for the given query words.
    """
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(q_words)
        results = searcher.search(query)

        # Collect results within the context manager
        output = []
        for r in results:
            output.append((r['url'], r['title']))  # Retrieve URL and title from stored fields

        return output


#logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def cook(soup_text):
    """tokenize the page's content using BeautifulSoup tool"""
    soup_text = soup_text.get_text(separator=' ')
    # FRAGE: 
    # Falls wir keine Zahlen dabei haben wollen?!
    #soup_is_ready = [word for word in re.findall(r'\b\w+\b', soup_text.lower()) if not word.isdigit()]
    soup_is_ready = re.findall(r'\b\w+\b', soup_text.lower())
    return soup_is_ready


def process_query(query):
    """ 
    Für die Query word können wir auch Tokenization, lemmization und so einfügen, 
    damit die suche besser wird, würde ich aber erst ganz am Ende machen, also in 2 wochen - je nachdem was
    wir noch so machen... und dann hier in die function!!!
    """
    return query.lower()

def index(url, word_to_urls, url_to_words, all_words):

    """
    Build an in-memory index of words to URLs, and extract the words for a URL.
    :param url: URL for which index shall be generated
    :word_to urls: list of URLS
    :url_to_words mapping: list of words on a page
    :all_words: total set of unique words across all pages
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    words = cook(soup)
    url_to_words[url] = words
    all_words.update(words)
    for word in set(words):
        word_to_urls[word].add(url)
    
    return soup

def crawl(initial_url):

    """
    Crawl a website and build index function, and store the words for each individual URL.
    
    :param initial_url: URL to start crawling from.
    :return: Tuple of two dictionaries
             - word-to-URLs index (word -> list of URLs)
             - URL-to-words mapping (URL -> list of words)
             - total set of unique words across all pages
    """

    visited = set()
    agenda = [initial_url]
    base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(initial_url))
    word_to_urls = defaultdict(set)
    url_to_words = {}
    all_words = set()

    # Open the writer for the duration of the crawl
    with ix.writer() as writer:
        while agenda:
            url = agenda.pop() # get next url
            if url in visited: # crawl if not visited yet
                continue

            visited.add(url) # mark as visited
            try:
                response = requests.get(url)
                if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                    # create index and extract page content (=soup)
                    soup = index(url, word_to_urls, url_to_words, all_words)

                    title = soup.title.string if soup.title else "No title"
                    content = soup.get_text(separator=' ')  # Get the textual content of the page
                    
                    add_to_index(writer, url, title, content)

                    for link in soup.find_all('a', href=True): # get all links on that page
                        absolute_url = urljoin(url, link['href'])
                        # if it fulfills the requirements and is not yet visited
                        if absolute_url.startswith(base_url) and absolute_url not in visited:
                            agenda.append(absolute_url) # append it to the agenda

            except requests.RequestException as e:
                logging.error(f"Failed to fetch: {url} Error: {e}")

    # return the words ad lists and number of uniqe words
    word_to_urls = {word: list(urls) for word, urls in word_to_urls.items()}
    return word_to_urls, url_to_words, all_words


def search(index, words):
    """
    Search for URLs containing all of the given words.

    :param index: The in-memory index (word -> list of URLs).
    :param words: List of words to search for.
    :return: List of URLs that contain all the words.
    """
    if not words:
        return []

    result_urls = set(index.get(words[0], []))  # get urls for the first word

    # intersect with urlss for each subsequent word
    for word in words[1:]:
        result_urls &= set(index.get(word, []))  # set intersection

    return list(result_urls)

if __name__ == "__main__":
    # initial url, url to be crawled
    initial_url = 'https://vm009.rz.uos.de/crawl/index.html'

    word_to_urls, url_to_words, all_words = crawl(initial_url)
    
    # Perform a search
    result = perform_search("symbol virgin")
    
    # Display the results
    print("Search Results:")
    for url, title in result:
        print(f"URL: {url}, Title: {title}")

