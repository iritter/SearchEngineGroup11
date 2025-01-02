from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.analysis import StemmingAnalyzer
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import os

# Whoosh StemmingAnalyzer 
stem_ana = StemmingAnalyzer()

# Schema for the index, specifies the fields, the analyzer and field_boost (weight)
schema = Schema(
    url=ID(stored=True), 
    title=TEXT(zanalyzer=stem_ana, stored=True, field_boost=2.5),
    h1_text=TEXT(analyzer=stem_ana, stored=True, field_boost=3.0),
    content=TEXT(analyzer=stem_ana, stored=True, field_boost=2.0), 
    keywords=KEYWORD(analyzer=stem_ana, stored=True, field_boost=1.0), 
    description=TEXT(analyzer=stem_ana, stored=True, field_boost=1.0)
)

# Create an index in the "indexdir" directory (the directory must already exist!)
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

# Create the index
ix = create_in("indexdir", schema)
writer = ix.writer()

# Write the index to the disk
writer.commit()

def add_to_index(writer, url, title, content, keywords, description, h1_text):
    """
    Adds a document to the Whoosh index
    Maps field names in the schema to the provided arguments
    Returns:
        None
    """
    writer.add_document(
        url=url, 
        title=title, 
        content=content, 
        keywords=keywords, 
        description=description, 
        h1_text=h1_text
    )


def crawl(initial_url):

    """
    Crawl a website and build index
    - starts with initial_url, stays in base domain
    - processes stored metadata of pages

    Param:
        initial_url (str): The starting URL for the crawl
    Returns:
        None
    """

    visited = set()
    agenda = [initial_url]
    base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(initial_url))

    # Open the writer for the duration of the crawl
    with ix.writer() as writer:
        while agenda:
            url = agenda.pop() # get next url
            if url in visited: # crawl if not visited yet
                continue

            visited.add(url) # mark as visited
            try:
                response = requests.get(url)
                # Ensure the response is valid and HTML content
                if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                    
                    # Ensure the correct encoding
                    response.encoding = response.apparent_encoding

                    # Create the BeautifulSoup object
                    soup = BeautifulSoup(response.text, 'html.parser')

                    for link in soup.find_all('a', href=True): # get all links on that page
                        absolute_url = urljoin(url, link['href'])
                        # if it fulfills the requirements and is not yet visited
                        if absolute_url.startswith(base_url) and absolute_url not in visited:
                            agenda.append(absolute_url) # append it to the agenda

                    # Extract the title
                    title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
                    print(f"Extracted Title: {title}")

                    # Extract h1
                    try:
                        body = soup.find('body')
                        h1 = body.find('h1') if body else None
                        h1_text = h1.get_text() if h1 else None

                    except Exception as e:
                        print(f"Error fetching {url}: {e}")
                        h1_text = None
                    
                    # Extract metadata keywords and description (if created)
                    keywords_meta = soup.find('meta', {'name': 'keywords'})
                    keywords = keywords_meta.get('content', "") if keywords_meta else "No keywords found"
                    print(f"Extracted Keywords: {keywords}")

                    description_meta = soup.find('meta', {'name': 'description'})
                    description = description_meta.get('content', "") if description_meta else "No description found"
                    print(f"Extracted Description: {description}")

                    # Remove a-tags
                    for a_tag in soup.find_all('a'):
                        a_tag.decompose()

                    # Extract the page content with BeautifulSoup
                    content = soup.get_text(separator=' ', strip=True)
                    
                    # Add the page to the index
                    add_to_index(writer, url, title, content, keywords, description, h1_text)

            except requests.RequestException as e:
                logging.error(f"Failed to fetch: {url} Error: {e}")
    return


if __name__ == "__main__":
    # url to be crawled
    initial_url = 'https://vm009.rz.uos.de/crawl/index.html'
    #initial_url = 'https://www.ikw.uni-osnabrueck.de/en/home.html'

    # start crawling
    crawl(initial_url)




