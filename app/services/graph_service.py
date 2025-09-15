from datetime import datetime
from typing import List, Dict
from pymongo import MongoClient
import collections

class GraphService:
    def __init__(self, db_uri: str, db_name: str):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]

    def bfs_shortest_path(self, start_id: str, end_id: str) -> List[str]:
        # Implement BFS to find the shortest path
        queue = collections.deque([(start_id, [start_id])])
        visited = set()
        while queue:
            current, path = queue.popleft()
            if current == end_id:
                return path
            if current not in visited:
                visited.add(current)
                neighbors = self.db.edges.find({'from': current})
                for neighbor in neighbors:
                    queue.append((neighbor['to'], path + [neighbor['to']]))
        return []

    def calculate_centrality(self, article_id: str) -> Dict[str, int]:
        # Calculate the degree centrality for a given article
        article = self.db.articles.find_one({'_id': article_id})
        if article:
            in_degree = self.db.edges.count_documents({'to': article_id})
            out_degree = self.db.edges.count_documents({'from': article_id})
            return {'in_degree': in_degree, 'out_degree': out_degree}
        return {'in_degree': 0, 'out_degree': 0}

    def start_crawl_session(self, user_id: str, start_node: str) -> str:
        session_id = f'{user_id}-{start_node}-{datetime.utcnow().isoformat()}'
        self.db.crawl_sessions.insert_one({
            '_id': session_id,
            'user_id': user_id,
            'start_node': start_node,
            'started_at': datetime.utcnow(),
            'status': 'active',
            'discovered_nodes': [],
            'metadata': {}
        })
        return session_id

    def update_crawl_session(self, session_id: str, discovered_node: str):
        self.db.crawl_sessions.update_one(
            {'_id': session_id},
            {'$addToSet': {'discovered_nodes': discovered_node}}
        )

    def cache_metrics(self, session_id: str, metrics: Dict):
        # Cache the calculated metrics
        pass
