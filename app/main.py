from fastapi import FastAPI, HTTPException
from typing import List
from app.services.crawl_service import CrawlService
from app.services.graph_service import GraphService
from app.repositories.article_repo import ArticleRepository
from app.repositories.edge_repo import EdgeRepository
from app.infrastructure.db import DB_URI, DB_NAME
import aiohttp
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize services and repositories
crawl_service = CrawlService(db_uri=DB_URI, db_name=DB_NAME)
graph_service = GraphService(db_uri=DB_URI, db_name=DB_NAME)
article_repo = ArticleRepository(db_uri=DB_URI, db_name=DB_NAME)
edge_repo = EdgeRepository(db_uri=DB_URI, db_name=DB_NAME)

async def fetch_wikipedia_articles(term: str) -> List[dict]:
    url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={term}&format=json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data.get('query', {}).get('search', [])

@app.get("/api/search", response_model=List[dict])
async def search_articles(term: str):
    articles = await fetch_wikipedia_articles(term)
    return [{"id": article['title'], "title": article['title'], "summary": article.get('snippet', '')} for article in articles]

async def fetch_article_links(article_title: str) -> dict:
    url = f'https://en.wikipedia.org/w/api.php?action=parse&page={article_title}&prop=links&format=json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data.get('parse', {}).get('links', [])

@app.get("/api/explore/{article_title}", response_model=dict)
async def explore_graph(article_title: str, depth: int = 1):
    article = article_repo.get_article_by_id(article_title)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
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
    explorations = article_repo.get_all_explorations()
    return explorations

@app.delete("/api/explorations/{exploration_id}", response_model=str)
async def delete_exploration(exploration_id: str):
    article_repo.delete_exploration(exploration_id)
    return exploration_id
