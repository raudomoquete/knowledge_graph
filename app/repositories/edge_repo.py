from pymongo import MongoClient

class EdgeRepository:
    def __init__(self, db_uri: str, db_name: str):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]

    def save_edge(self, from_id: str, to_id: str, anchor_text: str):
        # Logic to save edge data to the database
        self.db.edges.update_one(
            {'from': from_id, 'to': to_id},
            {'$set': {'anchor_text': anchor_text}},
            upsert=True
        )

    def get_edges_from_article(self, article_id: str) -> list:
        # Logic to retrieve edges from a given article
        return list(self.db.edges.find({'from': article_id}))
