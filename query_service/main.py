import logging
from fastapi import FastAPI, HTTPException, Body
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
    minio_client = MinioClient()
    mongo_client = MongoClientWrapper()
    advisor = SuperAdvisor()
    logger.info("Connected to MinIO, MongoDB, and OpenAI.")
    yield
    mongo_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/analyses")
async def list_analyzed_videos():
    try:
        files = minio_client.list_analyses()
        return {"count": len(files), "files": files}
    except Exception as e:
        logger.error(f"Failed to list files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Storage unavailable")

@app.get("/analyses/{video_id}")
async def get_analysis_by_id(video_id: str):
    filename = f"{video_id}-analysis.json"
    try:
        data = minio_client.get_analysis(filename)
        return data
    except S3Error:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        logger.error(f"Failed to retrieve {filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --- NEW: Super Advisor Endpoint ---
@app.post("/advisor")
async def get_super_advice(user_id: str = Body(...), query: str = Body(...)):
    """
    Super Advisor:
    1. Fetches user's emotional history from MongoDB.
    2. Analyzes current query + history using LLM.
    3. Returns 5 advices.
    """
    try:
        logger.info(f"Advisor requested for User: {user_id}")
        
        # 1. Get History
        history = mongo_client.get_user_history(user_id)
        
        # 2. Get Advice
        advice = advisor.get_advice(query, history)
        
        return advice
    except Exception as e:
        logger.error(f"Advisor failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Advisor unavailable")