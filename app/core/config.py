import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOSTNAME = os.getenv("DATABASE_HOSTNAME")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

DATABASE_URL_ASYNC = (
    f"postgresql+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"
)
DATABASE_URL_SYNC = (
    f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"
)

# File download location
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

# Celery Redis config (message broker)
REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=int(os.getenv("REDIS_PORT"))
#CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = (f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

#API_KEY=os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

MAX_DOWNLOADS_PER_DAY=int(os.getenv("MAX_DOWNLOADS_PER_DAY"))
MAX_VIDEO_SIZE=int(os.getenv("MAX_VIDEO_SIZE"))  
MAX_VIDEO_DURATION=int(os.getenv("MAX_VIDEO_DURATION"))   