import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import re
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def crawl_and_index(initial_url, max_depth=4):
    """
    Crawl a website and build an in-memory index of words to URLs, 
    as well as storing words for each individual URL.

    :param initial_url: URL to start crawling from.
    :param max_depth: Maximum depth to crawl.
    :return: Tuple of two dictionaries:
             - word-to-URLs index (word -> list of URLs)
             - URL-to-words mapping (URL -> list of words)
             - total set of unique words across all pages
    """

    visited = set()  # track visited urls 
    agenda = [(initial_url, 0)]  # store urls and their depth
    base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(initial_url))  # initial url
    word_to_urls = defaultdict(set)  # Word-to-URLs index
    url_to_words = {}  # url-to-words-mapping
    all_words = set()  

    while agenda:
        url, depth = agenda.pop()  # get next url and its depth
        if url in visited or depth > max_depth:  # skip if visited or depth exceeded
            continue

        logging.info(f"Crawling: {url}, Current Depth: {depth}")  

        try:
            response = requests.get(url) 

            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                logging.info(f"Processing: {url}, Depth: {depth}")  # successful processing
                visited.add(url)  # mark url/page as visited

                # parse the page content with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # extract text, remove punctuation and convert to lower 
                text = soup.get_text(separator=' ')  
                words = re.findall(r'\b\w+\b', text.lower()) 

                url_to_words[url] = set(words)  # store unique words for this page in a set
                all_words.update(words) # total number of unique words across all pages

                # update word-to-URLs index
                for word in words:
                    word_to_urls[word].add(url)

                # enqueue linked urls
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(url, href)  # resolve relative URLs
                    # enqueue the URL if it's within the same domain and not visited
                    if absolute_url.startswith(base_url) and absolute_url not in visited:
                        agenda.append((absolute_url, depth + 1))  # Increase depth by 1

            else:
                logging.warning(f"Skipping non-HTML or failed response for: {url}")  # skipped url
        except requests.RequestException as e:
            logging.error(f"Failed to fetch: {url} Error: {e}")  # fetch failure

    # convert sets to lists
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

    word_to_urls, url_to_words, all_words = crawl_and_index(initial_url, max_depth=3)
    logging.info(f"Indexing complete. Indexed {len(word_to_urls)} unique words.")
    
    # print out the unique words per page
    total_unique_words_count = len(all_words)  # number of total unique words across all pages
    logging.info(f"Total unique words across all pages: {total_unique_words_count}")
    
    for url, words in url_to_words.items():
        unique_words_count = len(words)  # Count unique words on that page
        logging.info(f"Words found on {url}: {words}")
        logging.info(f"Unique words on {url}: {unique_words_count}")
    
    # example of searching for multiple words
    search_words = ['world', 'pixels']
    result = search(word_to_urls, search_words)

    logging.info(f"Found {len(result)} URLs that contain all search words.")
    for url in result:  # display the found urls
        print(url)
