import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import re
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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


#### DEF MAIN
if __name__ == "__main__":
    # initial url, url to be crawled
    initial_url = 'https://vm009.rz.uos.de/crawl/index.html'

    word_to_urls, url_to_words, all_words = crawl(initial_url)
    logging.info(f"Indexing complete. Indexed {len(word_to_urls)} unique words.")
    
    # print out the unique words per page
    total_unique_words_count = len(all_words)  # number of total unique words across all pages
    logging.info(f"Total unique words across all pages: {total_unique_words_count}")
    
    for url, words in url_to_words.items():
        unique_words_count = len(words)  # Count unique words on that page
        logging.info(f"Words found on {url}: {words}")
        logging.info(f"Unique words on {url}: {unique_words_count}")
    
    # example of searching for multiple words
    search_words = ['symbol', 'virgin', 'grace']
    result = search(word_to_urls, search_words)

    logging.info(f"Found {len(result)} URLs that contain all search words.")
    for url in result:  # display the found urls
        print(url)
