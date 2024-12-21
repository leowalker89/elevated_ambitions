"""
Workflow for processing raw job listings into structured, enhanced descriptions.
Handles the elevation of job data through AI processing and validation.
"""

from typing import Optional, List, Dict
from datetime import datetime, UTC
from logfire import Logfire
from os import getenv
from dotenv import load_dotenv
import asyncio
from bson import ObjectId
from tqdm.asyncio import tqdm
from tqdm import tqdm as tqdm_sync

from backend.database import get_jobs_collection, get_elevated_jobs_collection
from backend.models.job_description_workflow_state import (
    JobDescriptionProcessingState,
    ProcessingStatusType
)
from backend.agents.job_description_graph import graph
from backend.models.job_description_models import JobDescription, GraderOutput

# Load environment variables
load_dotenv()

# Initialize logging with proper configuration
logger = Logfire()

# Default configuration
DEFAULT_BATCH_SIZE = 10
DEFAULT_MAX_CONCURRENT = 3
DEFAULT_MAX_RETRIES = 3

async def run_elevation_workflow(
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    job_titles: Optional[List[str]] = None
) -> Dict[str, int]:
    """Run the job elevation workflow with specified parameters."""
    batch_id = datetime.now(UTC).isoformat()
    
    # Remove bind() call and use direct logging
    logger.info("Starting batch elevation workflow",
        metadata={
            "batch_id": batch_id,
            "batch_size": batch_size,
            "max_concurrent": max_concurrent,
            "job_titles": job_titles
        }
    )
    
    logger.info(f"Starting job elevation workflow at {datetime.now(UTC)}")
    logger.info(f"Batch size: {batch_size}, Max concurrent: {max_concurrent}")
    
    try:
        # Get jobs collection
        jobs_collection = get_jobs_collection()
        
        # Use sync operations for simple queries
        total_docs = jobs_collection.count_documents({})
        logger.info(f"Total documents in job_listings collection: {total_docs}")
        
        if total_docs == 0:
            logger.warning("No documents found in job_listings collection!")
            return {"total": 0, "successful": 0, "failed": 0}
        
        # Build query for unprocessed jobs
        query = {
            "$or": [
                {"extracted": {"$ne": True}},
                {"extracted": {"$exists": False}}
            ]
        }
        if job_titles:
            query["title"] = {"$in": job_titles}
        
        logger.info(f"Searching with query: {query}")
        
        # Add sort by _id in descending order (-1) to get most recent first
        pending_jobs = list(
            jobs_collection.find(query)
            .sort("_id", -1)  # Sort by _id descending
            .limit(batch_size)
        )
        
        if not pending_jobs:
            logger.warning("No pending jobs found for elevation")
            sample_doc = jobs_collection.find_one({})  # Sync operation
            if sample_doc:
                logger.info("Sample document from collection:")
                logger.info(f"ID: {sample_doc.get('_id')}")
                logger.info(f"Title: {sample_doc.get('title')}")
            return {"total": 0, "successful": 0, "failed": 0}
            
        total_jobs = len(pending_jobs)
        logger.info(f"Found {total_jobs} jobs to process")
        logger.info(f"First job title: {pending_jobs[0].get('title', 'No title')}")
        
        # Create progress bar with correct total
        pbar = tqdm_sync(
            total=total_jobs,  # Uses actual number of jobs, not DEFAULT_BATCH_SIZE
            desc=f"Processing {total_jobs} jobs",
            unit="job"
        )
        
        # Process jobs with concurrency limit
        semaphore = asyncio.Semaphore(max_concurrent)
        stats = {"total": 0, "successful": 0, "failed": 0}
        
        async def process_with_semaphore(job: Dict) -> None:
            async with semaphore:
                try:
                    print(f"\nProcessing job: {job.get('title', 'No title')}")
                    result = await elevate_job_description(
                        job_id=str(job["_id"]),
                        raw_job_data=job,
                        max_retries=max_retries
                    )
                    
                    if result and result.status == ProcessingStatusType.COMPLETED:
                        stats["successful"] += 1
                        print(f"✓ Successfully processed job: {job.get('title', 'No title')}")
                    else:
                        stats["failed"] += 1
                        error_msg = result.error_message if result else "No result returned"
                        print(f"✗ Failed to process job: {job.get('title', 'No title')}")
                        print(f"Error: {error_msg}")
                        
                    stats["total"] += 1
                    pbar.update(1)
                    pbar.set_postfix(
                        successful=stats["successful"],
                        failed=stats["failed"]
                    )
                    
                    # Increase delay between jobs
                    await asyncio.sleep(10)  # Increased to 10 seconds
                    
                except Exception as e:
                    print(f"✗ Error processing job: {str(e)}")
                    print(f"Error type: {type(e).__name__}")
                    logger.error(f"Process error: {str(e)}", exc_info=True)  # Added full traceback
                    stats["failed"] += 1
                    stats["total"] += 1
                    pbar.update(1)
        
        # Create tasks for all jobs
        tasks = [process_with_semaphore(job) for job in pending_jobs]
        
        # Run all tasks
        await asyncio.gather(*tasks)
        pbar.close()
        
        logger.info(f"Job elevation workflow completed at {datetime.now(UTC)}")
        logger.info(f"Processed {stats['total']} jobs:")
        logger.info(f"- Successful: {stats['successful']}")
        logger.info(f"- Failed: {stats['failed']}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in elevation workflow: {str(e)}")
        return {"total": 0, "successful": 0, "failed": 0}

async def elevate_job_description(
    job_id: str,
    raw_job_data: Dict,
    max_retries: int = 3
) -> Optional[JobDescriptionProcessingState]:
    try:
        # Get MongoDB collections at the start
        elevated_jobs = get_elevated_jobs_collection()
        jobs_collection = get_jobs_collection()

        # Convert ObjectId to string in raw_job_data
        if '_id' in raw_job_data:
            raw_job_data = raw_job_data.copy()
            raw_job_data['_id'] = str(raw_job_data['_id'])

        initial_state = JobDescriptionProcessingState(
            job_id=job_id,
            raw_job_data=raw_job_data,
            status=ProcessingStatusType.EXTRACTING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        print("Starting graph processing...")
        final_state_dict = await graph.ainvoke(initial_state)
        print("Graph processing complete")
        
        print("\nDEBUG INFO:")
        print("-" * 50)
        print(f"State dict keys: {final_state_dict.keys()}")
        print(f"State dict values:")
        for key, value in final_state_dict.items():
            print(f"{key}: {type(value)}")
            if value is not None:
                print(f"Value: {value}")
        print("-" * 50)
        
        structured_job = final_state_dict.get('structured_job')
        grader_output = final_state_dict.get('grader_output')
        
        if not structured_job or not grader_output:
            print("✗ Missing required data from graph output")
            print(f"structured_job present: {structured_job is not None}")
            print(f"grader_output present: {grader_output is not None}")
            return JobDescriptionProcessingState(
                job_id=job_id,
                raw_job_data=raw_job_data,
                status=ProcessingStatusType.FAILED,
                error_message=f"Graph failed to produce complete data. Missing: {', '.join(k for k, v in {'structured_job': structured_job, 'grader_output': grader_output}.items() if not v)}",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )

        # Create final state and write to MongoDB
        try:
            final_state = JobDescriptionProcessingState(
                job_id=job_id,
                raw_job_data=raw_job_data,
                structured_job=structured_job,
                grader_output=grader_output,
                status=ProcessingStatusType.COMPLETED,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            
            # Write to MongoDB
            new_id = str(ObjectId())
            elevated_job = {
                "_id": new_id,
                "original_job_id": job_id,
                "structured_job": structured_job.model_dump(mode="json"),
                "grader_output": grader_output.model_dump(mode="json"),
                "created_at": datetime.now(UTC)
            }
            
            elevated_jobs.insert_one({"_id": ObjectId(new_id), **elevated_job})
            print("✓ Successfully inserted into elevated_jobs collection")
            
            jobs_collection.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": {
                    "extracted": True,
                    "elevated_job_id": new_id
                }}
            )
            print("✓ Updated original job")
            
            return final_state
            
        except Exception as e:
            print(f"✗ Error in final processing: {str(e)}")
            return JobDescriptionProcessingState(
                job_id=job_id,
                raw_job_data=raw_job_data,
                status=ProcessingStatusType.FAILED,
                error_message=str(e),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return None

if __name__ == "__main__":
    async def main():
        try:
            # Test MongoDB connection
            jobs_collection = get_jobs_collection()
            total_docs = jobs_collection.count_documents({})
            logger.info(f"Successfully connected to MongoDB. Total documents: {total_docs}")
            
            # Process batch of 100 jobs with NO concurrency
            stats = await run_elevation_workflow(
                batch_size=100,
                max_concurrent=1,  # Changed from 3 to 1
                max_retries=3
            )
            
            logger.info("Workflow complete")
            logger.info(f"Total processed: {stats['total']}")
            logger.info(f"Successful: {stats['successful']}")
            logger.info(f"Failed: {stats['failed']}")
            
        except Exception as e:
            logger.error(f"Error in main: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    asyncio.run(main())
