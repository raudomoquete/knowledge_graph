import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class Article:
    id: strawberry.ID
    slug: str
    lang: str
    title: str
    url: str
    summary: str
    last_crawled: datetime
    out_links: List[strawberry.ID]
    out_count: int
    in_count: int
    meta: dict

@strawberry.type
class Edge:
    id: strawberry.ID
    from_article: strawberry.ID
    to_article: strawberry.ID
    anchor_text: str
    context: str
    weight: int
    discovered_at: datetime

@strawberry.type
class CrawlSession:
    id: str
    user_id: str
    start_node: strawberry.ID
    started_at: datetime
    status: str
    discovered_nodes: List[strawberry.ID]
    metadata: dict

@strawberry.type
class MetricsCache:
    id: str
    session_id: str
    metric: str
    data: List[dict]
    computed_at: datetime

@strawberry.type
class Query:
    @strawberry.field
    def get_article(self, id: strawberry.ID) -> Optional[Article]:
        # Logic to retrieve an article by ID
        pass

    @strawberry.field
    def get_edge(self, id: strawberry.ID) -> Optional[Edge]:
        # Logic to retrieve an edge by ID
        pass

    @strawberry.field
    def get_crawl_session(self, id: str) -> Optional[CrawlSession]:
        # Logic to retrieve a crawl session by ID
        pass

    @strawberry.field
    def get_metrics_cache(self, id: str) -> Optional[MetricsCache]:
        # Logic to retrieve metrics cache by ID
        pass

schema = strawberry.Schema(query=Query)
