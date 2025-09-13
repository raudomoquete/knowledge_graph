from datetime import datetime
from typing import Dict, List
from pymongo import MongoClient

class MetricsService:
    def __init__(self, db_uri: str, db_name: str):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]

    def calculate_degree_centrality(self, article_id: str) -> Dict[str, int]:
        # Calculate the degree centrality for a given article
        article = self.db.articles.find_one({'_id': article_id})
        if article:
            return {
                'in_degree': article.get('in_count', 0),
                'out_degree': article.get('out_count', 0)
            }
        return {'in_degree': 0, 'out_degree': 0}

    def update_metrics_cache(self, session_id: str, metrics: Dict):
        # Update the metrics cache with new calculations
        self.db.metrics_cache.update_one(
            {'_id': f'{session_id}:degree-centrality'},
            {'$set': {'data': metrics, 'computed_at': datetime.utcnow()}},
            upsert=True
        )

    def get_real_time_metrics(self, session_id: str) -> List[Dict]:
        # Retrieve real-time metrics for a session
        cache = self.db.metrics_cache.find_one({'_id': f'{session_id}:degree-centrality'})
        return cache.get('data', []) if cache else []
