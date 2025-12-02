from pymongo import MongoClient
from config import settings

class MongoClientWrapper:
    def __init__(self):
       
        self.client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        self.db = self.client["therapy_db"]
        self.collection = self.db["session_analysis"]

    def save_analysis(self, user_id, video_id, analysis_data):
        """Saves the analysis with metadata for querying later"""
        document = {
            "user_id": user_id,
            "video_id": video_id,
            "analysis": analysis_data,
            
        }
        self.collection.insert_one(document)
        print(f"Saved analysis for {video_id} to MongoDB")

    def close(self):
        self.client.close()