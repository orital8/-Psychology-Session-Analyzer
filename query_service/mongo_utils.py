from pymongo import MongoClient
from config import settings

class MongoClientWrapper:
    def __init__(self):
        self.client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        self.db = self.client["therapy_db"]
        self.collection = self.db["session_analysis"]

    def get_user_history(self, user_id):
        """Fetches all past analyses for this user to build context for the Advisor"""
        cursor = self.collection.find({"user_id": user_id}, {"analysis": 1, "_id": 0})
        history = []
        for doc in cursor:
            if "analysis" in doc:
                history.append(doc["analysis"])
        return history

    def get_user_videos(self, user_id):
        """Fetches list of video IDs associated with a specific user"""
        cursor = self.collection.find({"user_id": user_id}, {"video_id": 1, "_id": 0})
        videos = [doc["video_id"] for doc in cursor if "video_id" in doc]
        return videos

    def close(self):
        self.client.close()