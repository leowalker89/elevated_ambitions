import asyncio
from datetime import datetime, UTC
from backend.workflows.elevate_job_descriptions import JobElevationWorkflow
from backend.database import get_jobs_collection
from backend.logging_config import setup_logging
from tqdm import tqdm


setup_logging()

async def process_jobs_with_rate_limit(
    max_jobs: int = 500,
    jobs_per_minute: int = 16,
    batch_size: int = 4
):
    """
    Process jobs with rate limiting.
    
    Args:
        max_jobs: Maximum number of jobs to process
        jobs_per_minute: Number of jobs to process per minute
        batch_size: Number of jobs to process in parallel
    """
    workflow = JobElevationWorkflow(batch_size=batch_size)
    await workflow.initialize()
    
    jobs_processed = 0
    delay = 60 / jobs_per_minute  # Seconds between each job
    
    while jobs_processed < max_jobs:
        # Get batch of unprocessed jobs
        stats = await workflow.process_batch(batch_size=batch_size)
        
        if stats["total"] == 0:
            print("No more jobs to process")
            break
            
        jobs_processed += stats["total"]
        print(f"Processed batch: {stats}")
        
        # Rate limiting delay
        await asyncio.sleep(delay * batch_size)
        
    return jobs_processed

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process jobs with rate limiting")
    parser.add_argument("--max-jobs", type=int, default=500)
    parser.add_argument("--jobs-per-minute", type=int, default=16)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    
    start_time = datetime.now(UTC)
    total_processed = await process_jobs_with_rate_limit(
        max_jobs=args.max_jobs,
        jobs_per_minute=args.jobs_per_minute,
        batch_size=args.batch_size
    )
    duration = datetime.now(UTC) - start_time
    
    print(f"\nProcessing complete:")
    print(f"Total jobs processed: {total_processed}")
    print(f"Time taken: {duration}")
    print(f"Average rate: {total_processed / duration.total_seconds() * 60:.1f} jobs/minute")

if __name__ == "__main__":
    asyncio.run(main()) 