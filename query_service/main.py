import logging
from fastapi import FastAPI, HTTPException, Body, Query
from contextlib import asynccontextmanager
from minio_utils import MinioClient
from mongo_utils import MongoClientWrapper
from llm_client import SuperAdvisor
from minio.error import S3Error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("query_service")

minio_client = None
mongo_client = None
advisor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global minio_client, mongo_client, advisor
    # Initialize connections (Let It Crash if infra is down)
    minio_client = MinioClient()
    mongo_client = MongoClientWrapper()
    advisor = SuperAdvisor()
    logger.info("Connected to MinIO, MongoDB, and OpenAI.")
    yield
    mongo_client.close()

app = FastAPI(lifespan=lifespan)

# --- Interactive Feature 1: Find My Videos ---
@app.get("/my-videos")
async def list_user_videos(user_id: str = Query(..., description="Enter your User ID to see your history")):
    """
    Returns a list of video IDs belonging to the specific user.
    Usage: /my-videos?user_id=22
    """
    try:
        videos = mongo_client.get_user_videos(user_id)
        if not videos:
            return {"message": "No videos found for this user.", "videos": [], "user_id": user_id}
        return {"user_id": user_id, "count": len(videos), "videos": videos}
    except Exception as e:
        logger.error(f"Failed to list videos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database unavailable")

# --- Interactive Feature 2: View Analysis ---
@app.get("/analyses/{video_id}")
async def get_analysis_by_id(video_id: str):
    """
    Returns the full psychological report for a specific video ID.
    User copies an ID from /my-videos and pastes it here.
    """
    filename = f"{video_id}-analysis.json"
    try:
        data = minio_client.get_analysis(filename)
        return data
    except S3Error:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        logger.error(f"Failed to retrieve {filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --- Interactive Feature 3: Super Advisor ---
@app.post("/advisor")
async def get_super_advice(user_id: str = Body(..., embed=True), query: str = Body(..., embed=True)):
    """
    Interactive Super Advisor:
    1. Reads user's emotional history from MongoDB.
    2. Sends history + current query to Psychology agent.
    3. Returns the advice immediately as JSON.
    """
    try:
        logger.info(f"Advisor requested for User: {user_id}")
        
        # 1. Fetch Context (History)
        history = mongo_client.get_user_history(user_id)
        
        # 2. Get Live Advice
        advice = advisor.get_advice(query, history)
        
        # 3. Return to User
        return advice
    except Exception as e:
        logger.error(f"Advisor failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Advisor unavailable")