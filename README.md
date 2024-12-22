# Search Engine Project

Welcome to our Search Engine Project! 🚀

This project is a simple, yet powerful search engine built using a combination of web crawling, indexing, and Flask. It enables users to search through the content of a domain that was crawled, with results presented in an intuitive and interactive way. Here's an overview of what we've built and how it works:

## 📑 **Table of Contents**

- [🔑 Key Features](#key-features)
- [⚙️ How It Works](#how-it-works)
  - [Home Route](#1-home-route)
  - [Search Results](#2-search-results)
  - [Example Flow](#example-flow)
- [🛠️ Tech Stack](#tech-stack)
- [🚀 Getting Started](#getting-started)
- [📂 Project Structure](#project-structure)
- [🌟 Enjoy the Game!](#-enjoy-the-game)
- [📝 Attribution](#-attribution)

## 🔑 Key Features

1. **🌐 Web Crawling**: We crawled a domain to gather web pages and extract their content. This was done with an efficient crawling mechanism that captures all the pages on the website.

2. **🔍 Indexing with Whoosh**: All the crawled pages are saved to an index directory using **Whoosh**—a fast, feature-rich full-text indexing and searching library in Python. This allows us to store and search the content of the pages quickly.

3. **🖥️ Flask Web Application**: A simple Flask app was created to make the search functionality accessible via a web interface. The home route lets users search for words or phrases, and the search results are displayed dynamically in a user-friendly way.

## How It Works

### 1. Home Route

When you visit the home page (`/home/`), you can enter one or more words in the search box. This is the entry point to your search experience. Simply type your query and click "Search." You can search for a word, or multiple words. In the latter case the application will find the intersection of pages that contain that word.
The application will process the input and send you to the results page.

### 2. Search Results

Once you submit your query, you're redirected to the `/search/` route where the magic happens! Here's what you'll find:

- **Clickable Links**: Each result comes with a link to the **original page**, so you can visit the site directly for more detailed information.

- **Additional Information**: In addition to clickable links, a **title, teaser, keywords and a summary** (description) are given for each search result, making it a better search experience. The teaser is an excerpt of the page content that contains the search term(s).

- **Highlighted Results**: Your search terms will be highlighted in **vibrant colors**, making them easy to identify. Highlights appear in both the teaser and the title, ensuring you can quickly locate relevant information.
  
- **Stemmming**: The application uses the Whoosh library's **StemmingAnalyzer** to match different forms of a word. For example, searching for "appearance" will also find results with "appeared" or "appear".

- **Number of Results**: We show you how many results were found for your search term(s), so you know the scope of the content you're dealing with.


### Example Flow

1. You visit the home page and enter a search term, like "Python programming."
2. After clicking "Search," you are taken to the `/search/` route.
3. The results show up with the title of each matching page, a teaser of the page containing your search words, the page keywords and description and the highlighteds search words.
4. The number of results is displayed at the top, and you can click on any result to view the original page.
5. At the top you can find a link to go back to the home page and make another search.

## Tech Stack

- **Python**: For the backend logic, crawling, and indexing.
- **Flask**: A lightweight web framework for handling the search requests and serving the web pages.
- **Whoosh**: A fast search engine library to index and search the crawled web pages.
- **HTML/CSS**: For styling the front-end and making the results visually appealing.

## Getting Started

To run this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/iritter/SearchEngineGroup11.git
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

4. Open your browser and visit `http://127.0.0.1:5500/` to start searching!

## 📂 **Project Structure**

```
SearchEngineGroup11/
|   .gitignore
|   README.md
|   requirements.txt
|
+---indexdir
|
+---py
|       crawlmitindex.py
|       flaskapp.py
|
+---static
|   \---css
|           styles.css
|   \---assets
|           header.png
|
\---templates
        base.html
        home.html
        not-found.html
        search.html

```
---

## 🌟 **Enjoy the Game!**

We hope you enjoyed using our **Search Engine**! 🔎🎉

### 📝 **Attribution**

Created with ❤️ by Group 11: Johanna, Christina & Isabel.
