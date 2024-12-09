#crawl with alternative words such as "virgin" and "virgins"
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import re
from collections import defaultdict
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# Initialize the stemmer and lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# Download necessary NLTK resources (if not already done)
nltk.download('wordnet')
nltk.download('omw-1.4')

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def process_word(word, use_stemming=False, use_lemmatization=False):
    """
    Process a single word by applying stemming or lemmatization.
    :param word: The word to be processed
    :param use_stemming: Whether to apply stemming
    :param use_lemmatization: Whether to apply lemmatization
    :return: Processed word
    """
    if use_stemming:
        return stemmer.stem(word)
    elif use_lemmatization:
        return lemmatizer.lemmatize(word)
    return word

def cook(soup_text, use_stemming=False, use_lemmatization=False):
    """Tokenize the page's content and apply stemming or lemmatization."""
    soup_text = soup_text.get_text(separator=' ')
    soup_is_ready = re.findall(r'\b\w+\b', soup_text.lower())  # tokenize text
    processed_words = [process_word(word, use_stemming, use_lemmatization) for word in soup_is_ready]
    return processed_words

def index(url, word_to_urls, url_to_words, all_words, use_stemming=False, use_lemmatization=False):
    """
    Build an in-memory index of words to URLs, and extract the words for a URL.
    :param url: URL for which index shall be generated
    :word_to_urls: list of URLS
    :url_to_words: mapping of words on a page
    :all_words: total set of unique words across all pages
    :param use_stemming: Whether to apply stemming
    :param use_lemmatization: Whether to apply lemmatization
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    words = cook(soup, use_stemming, use_lemmatization)
    url_to_words[url] = words
    all_words.update(words)
    for word in set(words):
        word_to_urls[word].add(url)

    return soup

def crawl(initial_url, use_stemming=False, use_lemmatization=False):
    """
    Crawl a website and build index function, and store the words for each individual URL.
    
    :param initial_url: URL to start crawling from.
    :param use_stemming: Whether to apply stemming.
    :param use_lemmatization: Whether to apply lemmatization.
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
        url = agenda.pop()  # get next url
        if url in visited:  # crawl if not visited yet
            continue

        visited.add(url)  # mark as visited
        try:
            response = requests.get(url)
            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                # create index and extract page content (=soup)
                soup = index(url, word_to_urls, url_to_words, all_words, use_stemming, use_lemmatization)

                for link in soup.find_all('a', href=True):  # get all links on that page
                    absolute_url = urljoin(url, link['href'])
                    # if it fulfills the requirements and is not yet visited
                    if absolute_url.startswith(base_url) and absolute_url not in visited:
                        agenda.append(absolute_url)  # append it to the agenda

        except requests.RequestException as e:
            logging.error(f"Failed to fetch: {url} Error: {e}")

    # return the words and lists and number of unique words
    word_to_urls = {word: list(urls) for word, urls in word_to_urls.items()}
    return word_to_urls, url_to_words, all_words

def search(index, words, use_stemming=False, use_lemmatization=False):
    """
    Search for URLs containing all of the given words.

    :param index: The in-memory index (word -> list of URLs).
    :param words: List of words to search for.
    :param use_stemming: Whether to apply stemming.
    :param use_lemmatization: Whether to apply lemmatization.
    :return: List of URLs that contain all the words.
    """
    if not words:
        return []

    # Process the query words with stemming/lemmatization
    processed_words = [process_word(word, use_stemming, use_lemmatization) for word in words]
    
    # Get URLs for the first processed word
    result_urls = set(index.get(processed_words[0], []))

    # Intersect with URLs for each subsequent word
    for word in processed_words[1:]:
        result_urls &= set(index.get(word, []))  # set intersection

    return list(result_urls)

#### DEF MAIN
if __name__ == "__main__":
    # initial url, url to be crawled
    initial_url = 'https://vm009.rz.uos.de/crawl/index.html'

    # Start crawling with lemmatization enabled (or change to use_stemming=True for stemming)
    word_to_urls, url_to_words, all_words = crawl(initial_url, use_lemmatization=True)

    logging.info(f"Indexing complete. Indexed {len(word_to_urls)} unique words.")
    
    # Print out the unique words per page
    total_unique_words_count = len(all_words)  # number of total unique words across all pages
    logging.info(f"Total unique words across all pages: {total_unique_words_count}")
    
    for url, words in url_to_words.items():
        unique_words_count = len(words)  # Count unique words on that page
        logging.info(f"Words found on {url}: {words}")
        logging.info(f"Unique words on {url}: {unique_words_count}")
    
    # Example of searching for multiple words (including "symbols" to test if "symbol" matches)
    search_words = ['symbol', 'virgin', 'grace', 'symbols', 'virgins', 'graced']
    result = search(word_to_urls, search_words, use_stemming=True)  # Ensure lemmatization is used

    logging.info(f"Found {len(result)} URLs that contain all search words.")
    for url in result:  # display the found urls
        print(url)
    #lemmatization does not understand past tense words and there is a way to fix but not sure if necessary 
    print("Query words after lemmatization:", [process_word(word, use_lemmatization=True) for word in search_words])
