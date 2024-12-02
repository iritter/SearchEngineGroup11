from bs4 import BeautifulSoup

h = "<html><head><title>The Title</title></head><body>Body content.</body></html>"

soup = BeautifulSoup(h, 'html.parser')
print(soup.html.body.text)
