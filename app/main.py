from fastapi import FastAPI, HTTPException
from typing import List
from app.services.crawl_service import CrawlService
from app.services.graph_service import GraphService
from app.repositories.article_repo import ArticleRepository
from app.repositories.edge_repo import EdgeRepository
from app.infrastructure.db import DB_URI, DB_NAME
import aiohttp
from fastapi.middleware.cors import CORSMiddleware
import logging
import wikipediaapi
import requests
import certifi
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)

# Disable SSL certificate verification temporarily
import requests
import certifi

# Ensure requests uses certifi's CA bundle
requests.adapters.DEFAULT_CA_BUNDLE_PATH = certifi.where()

app = FastAPI()

# Update CORS middleware to allow requests from http://localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allows requests from this specific origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize services and repositories
crawl_service = CrawlService(db_uri=DB_URI, db_name=DB_NAME)
graph_service = GraphService(db_uri=DB_URI, db_name=DB_NAME)
article_repo = ArticleRepository(db_uri=DB_URI, db_name=DB_NAME)
edge_repo = EdgeRepository(db_uri=DB_URI, db_name=DB_NAME)

# Initialize Wikipedia API client
wiki_wiki = wikipediaapi.Wikipedia('en')

# Add a User-Agent header to requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

async def fetch_wikipedia_articles(term: str) -> List[dict]:
    url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={term}&format=json'
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        try:
            data = response.json()
            return data.get('query', {}).get('search', [])
        except requests.exceptions.JSONDecodeError:
            logging.error("Failed to decode JSON from response")
            return []
    else:
        logging.error(f"Request failed with status code {response.status_code}")
        return []

@app.get("/api/search", response_model=List[dict])
async def search_articles(term: str):
    articles = await fetch_wikipedia_articles(term)
    return [{"id": article['title'], "title": article['title'], "summary": article.get('snippet', '')} for article in articles]

# Use requests to fetch article links with SSL verification disabled
async def fetch_article_links(article_title: str) -> dict:
    url = f'https://en.wikipedia.org/w/api.php?action=parse&page={article_title}&prop=links&format=json'
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        try:
            data = response.json()
            links = data.get('parse', {}).get('links', [])
            return [{"id": link['*'], "label": link['*'], "summary": ""} for link in links if link.get('ns') == 0]
        except requests.exceptions.JSONDecodeError:
            logging.error("Failed to decode JSON from response")
            return []
    else:
        logging.error(f"Request failed with status code {response.status_code}")
        return []

# Modify the explore endpoint to clean the HTML summary
@app.get("/api/explore/{article_title}", response_model=dict)
async def explore_graph(article_title: str, depth: int = 1):
    # Try to get the article from the database
    article = article_repo.get_article_by_id(article_title)
    if not article:
        # Fetch the article from Wikipedia if not found
        url = f'https://en.wikipedia.org/w/api.php?action=parse&page={article_title}&prop=text&format=json'
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            try:
                data = response.json()
                page = data.get('parse', {})
                html_content = page.get('text', {}).get('*', '')
                # Use BeautifulSoup to extract plain text
                soup = BeautifulSoup(html_content, 'html.parser')
                summary = soup.get_text()[:200]  # Get a snippet of the article
                article = {
                    '_id': article_title,
                    'title': page.get('title', article_title),
                    'summary': summary,
                }
                # Store the article in the database
                article_repo.save_article(article)
            except requests.exceptions.JSONDecodeError:
                logging.error("Failed to decode JSON from response")
                raise HTTPException(status_code=500, detail="Error fetching article from Wikipedia")
        else:
            logging.error(f"Request failed with status code {response.status_code}")
            raise HTTPException(status_code=404, detail="Article not found")
    # Fetch links from the article
    links = await fetch_article_links(article_title)
    nodes = [{"id": article_title, "label": article_title, "summary": article.get('summary', '')}]
    edges = []
    for link in links:
        if link.get('ns') == 0:  # Only consider links to other articles
            nodes.append({"id": link['*'], "label": link['*'], "summary": ""})
            edges.append({"from": article_title, "to": link['*']})
    return {"nodes": nodes, "edges": edges}

@app.post("/api/explorations", response_model=str)
async def save_exploration(exploration_data: dict):
    exploration_id = article_repo.save_article(exploration_data)
    return exploration_id

@app.get("/api/explorations", response_model=List[dict])
async def list_explorations():
    # Retrieve all articles as explorations
    explorations = article_repo.get_all_explorations()
    return explorations

@app.delete("/api/explorations/{exploration_id}", response_model=str)
async def delete_exploration(exploration_id: str):
    article_repo.delete_exploration(exploration_id)
    return exploration_id
