from pymongo import MongoClient

class ArticleRepository:
    def __init__(self, db_uri: str, db_name: str):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]

    def save_article(self, article_data: dict):
        # Logic to save article data to the database
        self.db.articles.update_one(
            {'_id': article_data['_id']},
            {'$set': article_data},
            upsert=True
        )

    def get_article_by_id(self, article_id: str) -> dict:
        # Logic to retrieve an article by ID
        return self.db.articles.find_one({'_id': article_id})
