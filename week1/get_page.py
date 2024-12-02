import requests

r = requests.get('https://spiegel.de')
                 
print(r.status_code)
print(r.headers)
print(r.text)