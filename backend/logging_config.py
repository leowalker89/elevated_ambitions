from logfire import configure
from os import getenv
import os
from dotenv import load_dotenv

def setup_logging():
    """Configure logging with fallback options."""
    load_dotenv()
    try:
        api_key = getenv("LOGFIRE_API_KEY")
        if not api_key:
            raise ValueError("LOGFIRE_API_KEY not found in environment")
            
        configure(
            token=api_key,
        )
    except Exception as e:
        print(f"Warning: Failed to configure Logfire: {e}")
        os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "1" 