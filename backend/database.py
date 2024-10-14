import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
print(f"MONGODB_URL: {MONGODB_URL}")  # Debugging - to check if the env variable is loaded

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Connect to the MongoDB database
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=20000)
    
    # Specify the database name
    db = client.polls_app  # Use the database named polls_app
    print(db)

    # Check connection
    client.admin.command('ping')
    logger.info("Successfully connected to the MongoDB database.")

    if 'users' not in db.list_collection_names():
        db.create_collection('users')
        logger.info("Created 'users' collection.")
    else:
        logger.info("'users' collection already exists.")
    if 'polls' not in db.list_collection_names():
        db.create_collection('polls')
        logger.info("Created 'polls' collection.")
    else:
        logger.info("'polls' collection already exists.")
except ServerSelectionTimeoutError as e:
    logger.error(f"Failed to connect to the MongoDB database: {str(e)}")
except Exception as e:
    logger.error(f"An unexpected error occurred: {str(e)}")
