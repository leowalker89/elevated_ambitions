"""
MongoDB connection and collection management module.
Provides singleton connection manager and collection access functions.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv
import os
from logfire import Logfire, configure
from os import getenv
from backend.logging_config import setup_logging
import asyncio

setup_logging()  # Call this before any logger usage

# Initialize logging
logger = Logfire()

class MongoDB:
    """
    MongoDB connection manager implementing singleton pattern.
    
    Manages database connection and provides access to collections.
    Ensures single database connection is maintained throughout the application.
    """
    _instance: Optional['MongoDB'] = None
    _client: Optional[AsyncIOMotorClient] = None
    
    def __new__(cls):
        """Singleton pattern to ensure single database connection"""
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Async connection initialization"""
        if self._client is None:
            await self._connect()
    
    async def _connect(self):
        """Async MongoDB connection setup"""
        load_dotenv()
        
        uri = os.getenv('MONGODB_URI')
        if not uri:
            raise ValueError("MongoDB URI not found in environment variables")
        
        masked_uri = uri.replace(os.getenv('MONGODB_PASSWORD', ''), '***')
        logger.info(f"Attempting to connect with URI: {masked_uri}")
        
        try:
            self._client = AsyncIOMotorClient(
                uri,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            await self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def get_collection(self, db_name: str, collection_name: str):
        """Get MongoDB collection with async connection handling"""
        if not self._client:
            await self.connect()
        return self._client[db_name][collection_name]
    
    def close(self):
        """Close MongoDB connection and cleanup resources."""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("MongoDB connection closed")

# Create singleton instance
mongodb = MongoDB()

async def get_jobs_collection():
    """
    Get the jobs collection from MongoDB.
    
    Returns:
        Collection: MongoDB collection for storing job listings
    """
    return await mongodb.get_collection('jobs_db', 'job_listings')

async def get_searches_collection():
    """
    Get the searches collection from MongoDB.
    
    Returns:
        Collection: MongoDB collection for storing job search metadata
    """
    return await mongodb.get_collection('jobs_db', 'job_searches')

async def get_elevated_jobs_collection():
    """
    Get the elevated jobs collection from MongoDB.
    Stores standardized and enriched job descriptions after processing.
    
    Returns:
        Collection: MongoDB collection for storing processed job listings
    """
    return await mongodb.get_collection('jobs_db', 'elevated_jobs')

__all__ = ['mongodb', 'get_jobs_collection', 'get_searches_collection', 'get_elevated_jobs_collection'] 