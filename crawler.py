import requests
from bs4 import BeautifulSoup
import pysolr
import time

solr_url = 'http://localhost:8983/solr/crawler'
solr = pysolr.Solr(solr_url, always_commit=True)
def crawl_google_scholar(query):
    base_url = f'https://scholar.google.com/scholar?q={query}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('div', class_='gs_ri')

        for result in results:
            title = result.find('h3', class_='gs_rt').text
            url = result.find('a')['href']
            authors = result.find('div', class_='gs_a').text
            snippet = result.find('div', class_='gs_rs').text

            # solr
            index_data_to_solr({
                'title': title,
                'url': url,
                'authors': authors,
                'snippet': snippet
            })

    else:
        print(f'Failed to crawl {query}. Status code: {response.status_code}')

def index_data_to_solr(data):
    doc = {
        'title': data['title'],
        'url': data['url'],
        'authors': data['authors'],
        'snippet': data['snippet']
    }

    solr.add([doc])

base_queries = ['machine learning techniques', 'data science', 'artificial intelligence']
queries_count = 0

for query in base_queries:
    crawl_google_scholar(query)
    queries_count += 1
    if queries_count >= 1000:
        break
    time.sleep(10) 
