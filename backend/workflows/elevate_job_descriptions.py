"""
Workflow for processing raw job listings into structured, enhanced descriptions.
Handles the elevation of job data through AI processing and validation.
"""

from typing import Optional, List, Dict
from datetime import datetime, UTC
from logfire import Logfire, configure
from pydantic import Field
import asyncio
from bson import ObjectId
from tqdm.asyncio import tqdm
from tqdm import tqdm as tqdm_sync
from os import getenv

from backend.database import get_jobs_collection, get_elevated_jobs_collection
from backend.models.job_description_workflow_state import JobDescriptionProcessingState
from backend.agents.job_description_graph import create_job_description_graph
from backend.logging_config import setup_logging

setup_logging()  # Must be before any other imports that might use logging

class JobElevationWorkflow:
    """
    Orchestrates the complete job elevation process, including:
    - Batch processing of jobs
    - Concurrent execution management
    - Database operations
    - Error handling and retries
    """
    
    def __init__(self, batch_size: int = 10, max_concurrent: int = 3):
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.graph = create_job_description_graph()
        self.logger = Logfire()
        self.jobs_collection = None
        self.elevated_jobs = None

    async def initialize(self):
        """Initialize async resources"""
        self.jobs_collection = await get_jobs_collection()
        self.elevated_jobs = await get_elevated_jobs_collection()

    async def process_job(self, job_id: str, raw_job_data: Dict) -> JobDescriptionProcessingState:
        """Process a single job through the elevation workflow."""
        try:
            # Convert ObjectId to string in raw_job_data
            if '_id' in raw_job_data:
                raw_job_data = raw_job_data.copy()
                raw_job_data['_id'] = str(raw_job_data['_id'])

            initial_state = JobDescriptionProcessingState(
                job_id=job_id,
                raw_job_data=raw_job_data,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            
            self.logger.info("Starting job processing", metadata={
                "job_id": job_id,
                "initial_status": initial_state.status
            })
            
            # Execute the graph and convert result back to JobDescriptionProcessingState
            result = await self.graph.ainvoke(initial_state)
            final_state = JobDescriptionProcessingState(**result) if isinstance(result, dict) else result
            
            self.logger.info("Completed job processing", metadata={
                "job_id": job_id,
                "final_status": final_state.status,
                "attempts": final_state.attempts,
                "quality_score": final_state.grader_output.overall_quality_score if final_state.grader_output else None
            })
            
            if final_state.status == "completed":
                await self._save_to_database(final_state)
            
            return final_state
            
        except Exception as e:
            self.logger.error(f"Error processing job {job_id}: {str(e)}", exc_info=True)
            return JobDescriptionProcessingState(
                job_id=job_id,
                raw_job_data=raw_job_data,
                status="failed",
                error_message=str(e),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )

    async def process_batch(
        self,
        batch_size: Optional[int] = None,
        max_concurrent: Optional[int] = None,
        job_titles: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Process a batch of jobs with concurrency control."""
        batch_size = batch_size or self.batch_size
        max_concurrent = max_concurrent or self.max_concurrent
        
        self.logger.info("Starting batch processing", 
            metadata={
                "batch_size": batch_size,
                "max_concurrent": max_concurrent,
                "job_titles": job_titles
            }
        )
        
        # Get pending jobs
        query = {
            "$or": [
                {"extracted": {"$ne": True}},
                {"extracted": {"$exists": False}}
            ]
        }
        if job_titles:
            query["title"] = {"$in": job_titles}
            
        # Use to_list() for async cursor operation
        pending_jobs = await self.jobs_collection.find(query) \
            .sort("_id", -1) \
            .limit(batch_size) \
            .to_list(length=batch_size)
        
        if not pending_jobs:
            return {"total": 0, "successful": 0, "failed": 0}
        
        # Process with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        stats = {"total": 0, "successful": 0, "failed": 0}
        
        async def process_with_semaphore(job: Dict):
            async with semaphore:
                result = await self.process_job(str(job["_id"]), job)
                if result.status == "completed":
                    stats["successful"] += 1
                else:
                    stats["failed"] += 1
                stats["total"] += 1
        
        # Process all jobs with progress bar
        tasks = [process_with_semaphore(job) for job in pending_jobs]
        with tqdm_sync(total=len(tasks), desc="Processing jobs") as pbar:
            for coro in asyncio.as_completed(tasks):
                await coro
                pbar.update(1)
        
        return stats

    async def _save_to_database(self, state: JobDescriptionProcessingState):
        """Save processed job to database."""
        try:
            new_id = str(ObjectId())
            elevated_job = {
                "_id": ObjectId(new_id),
                "original_job_id": state.job_id,
                "structured_job": state.structured_job.model_dump(mode="json"),
                "grader_output": state.grader_output.model_dump(mode="json"),
                "created_at": datetime.now(UTC)
            }
            
            await self.elevated_jobs.insert_one(elevated_job)
            
            await self.jobs_collection.update_one(
                {"_id": ObjectId(state.job_id)},
                {"$set": {
                    "extracted": True,
                    "elevated_job_id": new_id
                }}
            )
            
            self.logger.info("Saved elevated job to database", metadata={
                "job_id": state.job_id,
                "elevated_job_id": new_id
            })
            
        except Exception as e:
            self.logger.error(f"Failed to save job to database: {str(e)}", metadata={
                "job_id": state.job_id
            })
            raise

async def main():
    """CLI entry point for the workflow."""
    import argparse
    parser = argparse.ArgumentParser(description="Job Elevation Workflow")
    parser.add_argument("--batch-size", type=int, help="Batch size for processing")
    parser.add_argument("--max-concurrent", type=int, help="Maximum concurrent jobs")
    parser.add_argument("--job-titles", nargs="+", help="Specific job titles to process")
    args = parser.parse_args()
    
    workflow = JobElevationWorkflow()
    await workflow.initialize()  # Initialize collections
    stats = await workflow.process_batch(
        batch_size=args.batch_size,
        max_concurrent=args.max_concurrent,
        job_titles=args.job_titles
    )
    
    workflow.logger.info("Workflow complete", metadata=stats)

if __name__ == "__main__":
    asyncio.run(main())
