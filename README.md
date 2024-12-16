# Search Engine Project

Welcome to our Search Engine Project! 🚀

This project is a simple, yet powerful search engine built using a combination of web crawling, indexing, and Flask. It enables users to search through the content of a domain that was crawled, with results presented in an intuitive and interactive way. Here's an overview of what we've built and how it works:

## 📑 **Table of Contents**

- [Key Features](#key-features)
- [How It Works](#how-it-works)
  - [Home Route](#1-home-route)
  - [Search Results](#2-search-results)
  - [Example Flow](#example-flow)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [📂 Project Structure](#project-structure)
- [🌟 Enjoy the Game!](#-enjoy-the-game)
- [📝 Attribution](#-attribution)

## Key Features

1. **Web Crawling**: We crawled a domain to gather web pages and extract their content. This was done with an efficient crawling mechanism that captures all the pages on the website.

2. **Indexing with Whoosh**: All the crawled pages are saved to an index directory using **Whoosh**—a fast, feature-rich full-text indexing and searching library in Python. This allows us to store and search the content of the pages quickly.

3. **Flask Web Application**: A simple Flask app was created to make the search functionality accessible via a web interface. The home route lets users search for words or phrases, and the search results are displayed dynamically in a user-friendly way.

## How It Works

### 1. Home Route

When you visit the home page (`/home/`), you can enter one or more words in the search box. This is the entry point to your search experience. Simply type your query and click "Search." The application will process the input and send you to the results page.

### 2. Search Results

Once you submit your query, you're redirected to the `/search/` route where the magic happens! Here's what you'll find:

- **Highlighted Results**: For each page in the results, the title and a teaser of the content will be displayed. The words you searched for will be **highlighted** in bold so you can easily spot their occurrence.
  
- **Number of Results**: We show you how many results were found for your search term(s), so you know the scope of the content you're dealing with.

- **Clickable Links**: Each result comes with a link to the original page, so you can visit the site directly for more detailed information.

### Example Flow

1. You visit the home page and enter a search term, like "Python programming."
2. After clicking "Search," you are taken to the `/search/` route.
3. The results show up with the title of each matching page, a snippet of the page containing your search words, and those words are highlighted.
4. The number of results is displayed at the top, and you can click on any result to view the original page.

## Tech Stack

- **Python**: For the backend logic, crawling, and indexing.
- **Flask**: A lightweight web framework for handling the search requests and serving the web pages.
- **Whoosh**: A fast search engine library to index and search the crawled web pages.
- **HTML/CSS**: For styling the front-end and making the results visually appealing.

## Getting Started

To run this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/search-engine-project.git
    cd search-engine-project
    ```

2. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask app:
    ```bash
    python app.py
    ```

4. Open your browser and visit `http://127.0.0.1:5000/` to start searching!

## 📂 **Project Structure**

```
SearchEngineGroup11/
|   .gitignore
|   README.md
|   requirements.txt
|
+---py
|       crawlmitindex.py
|       flaskapp.py
|
+---static
|   \---css
|           highlight.css
|           styles.css
|
\---templates
        base.html
        home.html
        not-found.html
        search.html

```
---

## Tech Stack

- **Python**: For the backend logic, crawling, and indexing.
- **Flask**: A lightweight web framework for handling the search requests and serving the web pages.
- **Whoosh**: A fast search engine library to index and search the crawled web pages.
- **HTML/CSS**: For styling the front-end and making the results visually appealing.

## Getting Started

To run this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/search-engine-project.git
    cd search-engine-project
    ```

2. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask app:
    ```bash
    python app.py
    ```

4. Open your browser and visit `http://127.0.0.1:5000/` to start searching!

## Conclusion

This project demonstrates the power of combining web crawling, full-text search indexing, and web development to create a simple search engine. It provides an interactive and informative way to explore content on the web, all in a user-friendly format. Whether you're looking for specific information or just browsing, this search engine makes it easy to find exactly what you're looking for.

We hope you enjoyed using our **Search Engine**! 🔎🎉

### 📝 **Attribution**

Created with ❤️ by Group 11: Johanna, Christina & Isabel.
