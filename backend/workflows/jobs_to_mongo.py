"""
Workflow for fetching job listings and storing them in MongoDB.
Handles batch processing of multiple job searches with rate limiting.
"""

from typing import List, Tuple, Optional
from backend.utils.job_search import fetch_and_parse_jobs, store_job_results
from logfire import Logfire
import asyncio
import aiohttp
import time
from datetime import datetime, UTC
import random
from itertools import product
from tqdm.asyncio import tqdm
from tqdm import tqdm as tqdm_sync

# Initialize logging
logger = Logfire()

# Job search configurations
JOB_TITLES: List[str] = [
    "AI Engineer", "Applied Data Scientist", "Machine Learning Engineer",
    "Technical Program Manager", "Solutions Engineer",
]

JOB_LOCATIONS: List[str] = [
    "Palo Alto CA", "Mountain View CA", "Sunnyvale CA", "San Jose CA",
    "San Francisco CA", "Fremont CA", "Redwood City CA", "Remote"   
]

TECH_HUBS: List[str] = [
    "Seattle WA", "Austin TX", "Dallas TX", "Miami FL", "New York NY",
    "Denver CO", "Charlotte NC", "Northern Virginia"
]

class RateLimiter:
    """Rate limiter for API calls"""
    def __init__(self, calls_per_minute: int = 30):
        self.calls_per_minute = calls_per_minute
        self.interval = 60 / calls_per_minute
        self.last_call = 0
    
    async def wait(self):
        """Wait appropriate time to maintain rate limit"""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.interval:
            await asyncio.sleep(self.interval - elapsed)
        self.last_call = time.time()

async def process_search(
    job_title: str,
    location: str,
    rate_limiter: RateLimiter,
    max_retries: int = 3,
    max_search_level: int = 2  # Add max search level parameter
) -> bool:
    """
    Process a single job search asynchronously with pagination
    
    Args:
        job_title: Job title to search for
        location: Location to search in
        rate_limiter: Rate limiter instance
        max_retries: Maximum number of retry attempts
        max_search_level: Maximum pagination level to fetch
    """
    retries = 0
    current_level = 1
    next_token = None
    
    while retries < max_retries and current_level <= max_search_level:
        try:
            await rate_limiter.wait()
            logger.info(f"Searching for {job_title} in {location} (Level {current_level})")
            
            parsed_result = fetch_and_parse_jobs(
                job_title=job_title,
                job_location=location,
                next_page_token=next_token,
                search_level=current_level
            )
            
            if parsed_result and store_job_results(parsed_result):
                logger.info(f"Successfully stored {len(parsed_result.jobs)} jobs for {job_title} in {location} (Level {current_level})")
                
                # Check if we have more pages and should continue
                if (parsed_result.pagination and 
                    parsed_result.pagination.next_page_token and 
                    current_level < max_search_level):
                    next_token = parsed_result.pagination.next_page_token
                    current_level += 1
                    # Reset retries for next page
                    retries = 0
                    # Add delay before next page request
                    await asyncio.sleep(random.uniform(1, 3))
                    continue
                
                return True
                
            retries += 1
            if retries < max_retries:
                delay = random.uniform(1, 3)
                await asyncio.sleep(delay)
                
        except Exception as e:
            logger.error(f"Error processing search for {job_title} in {location} (Level {current_level}): {str(e)}")
            retries += 1
            if retries < max_retries:
                await asyncio.sleep(2 ** retries)  # Exponential backoff
    
    logger.error(f"Failed to process search for {job_title} in {location} after {max_retries} attempts")
    return False

async def process_job_searches(
    job_titles: List[str],
    job_locations: List[str],
    max_concurrent: int = 3,
    calls_per_minute: int = 30,
    max_retries: int = 3,
    max_search_level: int = 2  # Add max search level parameter
) -> Tuple[int, int]:
    """Process job searches asynchronously with rate limiting and progress bar"""
    rate_limiter = RateLimiter(calls_per_minute)
    semaphore = asyncio.Semaphore(max_concurrent)
    successful = 0
    failed = 0
    
    total_combinations = len(job_titles) * len(job_locations)
    logger.info(f"Starting job search batch processing at {datetime.now(UTC)}")
    logger.info(f"Processing {total_combinations} combinations")
    
    # Create progress bar
    pbar = tqdm_sync(
        total=total_combinations,
        desc="Processing job searches",
        unit="search",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    )
    
    async def bounded_search(job_title: str, location: str) -> None:
        """Execute search with semaphore bound and update progress"""
        nonlocal successful, failed
        async with semaphore:
            if await process_search(job_title, location, rate_limiter, max_retries, max_search_level):
                successful += 1
            else:
                failed += 1
            pbar.update(1)
            pbar.set_postfix(
                successful=successful,
                failed=failed,
                current=f"{job_title} in {location}"
            )
    
    try:
        # Create tasks for all combinations
        tasks = [
            bounded_search(title, location)
            for title, location in product(job_titles, job_locations)
        ]
        
        # Run all tasks
        await asyncio.gather(*tasks)
        
    finally:
        pbar.close()
    
    logger.info(f"Job search batch processing completed at {datetime.now(UTC)}")
    logger.info(f"Successful searches: {successful}")
    logger.info(f"Failed searches: {failed}")
    
    return successful, failed

def run_job_search_workflow(
    job_titles: Optional[List[str]] = None,
    job_locations: Optional[List[str]] = None,
    max_concurrent: int = 3,
    calls_per_minute: int = 30,
    max_retries: int = 3,
    max_search_level: int = 2  # Add max search level parameter
) -> None:
    """
    Run the job search workflow
    
    Args:
        job_titles: Optional custom list of job titles
        job_locations: Optional custom list of locations
        max_concurrent: Maximum number of concurrent requests
        calls_per_minute: Maximum API calls per minute
        max_retries: Maximum retry attempts per search
        max_search_level: Maximum pagination level to fetch (default: 2)
    """
    titles = job_titles if job_titles is not None else JOB_TITLES
    locations = job_locations if job_locations is not None else JOB_LOCATIONS
    
    asyncio.run(process_job_searches(
        titles,
        locations,
        max_concurrent=max_concurrent,
        calls_per_minute=calls_per_minute,
        max_retries=max_retries,
        max_search_level=max_search_level
    ))

if __name__ == "__main__":
    # Test the workflow
    run_job_search_workflow(
        max_concurrent=3,  # Maximum concurrent requests
        calls_per_minute=30,  # Rate limit
        max_retries=3,  # Maximum retries per search
        max_search_level=2  # Maximum pagination level to fetch
    )
