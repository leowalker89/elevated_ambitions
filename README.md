# Elevated Ambitions

A comprehensive AI-powered platform that transforms the job search and career development process. By combining advanced job search capabilities with intelligent processing, we help both job seekers and employers make better matches.

## Overview

Elevated Ambitions uses AI to:
- Collect and analyze job postings from across the internet
- Structure and standardize job descriptions
- Extract key requirements and qualifications
- Grade job postings for completeness and clarity
- Match candidates with suitable positions (coming soon)

## Key Features

### Job Collection & Processing
- Automated job searching using Google Jobs API
- Rate-limited batch processing
- Structured data storage in MongoDB
- Concurrent processing capabilities

### AI-Powered Analysis
- Intelligent job description parsing
- Standardized format conversion
- Quality assessment and grading
- Requirement extraction and categorization

### Development Features (Coming Soon)
- Resume parsing and analysis
- Interview question generation
- Skill gap analysis
- Career path recommendations

## Project Structure

```
elevated_ambitions/
├── backend/
│   ├── agents/              # AI processing agents and workflow nodes
│   │   ├── nodes.py        # Core processing nodes for job analysis
│   │   └── job_description_graph.py  # Workflow graph definition
│   │
│   ├── database/           # Database connectivity and management
│   │   ├── __init__.py
│   │   └── mongodb.py      # MongoDB connection and collections
│   │
│   ├── models/             # Pydantic data models
│   │   ├── job_description_models.py
│   │   ├── job_description_workflow_state.py
│   │   └── jobs_search_models.py
│   │
│   ├── notebooks/          # Development and testing notebooks
│   │   ├── google_talent.ipynb
│   │   └── Resume_Parser.ipynb
│   │
│   ├── tests/              # Test suite
│   │   ├── test_nodes.py
│   │   └── test_extraction_graph.py
│   │
│   └── workflows/          # Core business logic
│       ├── jobs_to_mongo.py
│       └── job_elevation_workflow.py
│
├── templates/              # JSON templates and schemas
├── Dockerfile             # Container definition
├── docker-compose.yml     # Service orchestration
└── pyproject.toml         # Project dependencies and config
```

### Key Components

- **agents/**: Contains the AI processing logic and workflow definitions
- **database/**: Handles all database operations and connections
- **models/**: Defines data structures using Pydantic
- **workflows/**: Implements core business logic and processing pipelines
- **tests/**: Comprehensive test suite
- **notebooks/**: Development and experimentation environment

## Setup & Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- uv (Modern Python package installer)

### Environment Configuration

1. Clone the repository:
```bash
git clone https://github.com/yourusername/elevated_ambitions.git
cd elevated_ambitions
```

2. Create a `.env` file in the root directory with the following variables:
```bash
MONGODB_URI=your_mongodb_uri
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=your_project_name
LANGCHAIN_TRACING_V2=true
```

### Development Setup

1. Create and activate a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
uv pip install -e .
```

### Docker Setup

1. Build and start the services:
```bash
docker-compose up -d
```

2. Verify services are running:
```bash
docker-compose ps
```

The application runs in Docker containers with:
- A Python application container
- MongoDB for data storage
- Automatic environment configuration
- Volume mounting for development

Would you like me to continue with the usage section next?

## Usage

### Job Search and Collection

```python
from backend.workflows.jobs_to_mongo import run_job_search_workflow

# Run a job search with custom parameters
await run_job_search_workflow(
    job_titles=["AI Engineer", "Machine Learning Engineer"],
    job_locations=["San Francisco CA", "Seattle WA"],
    max_concurrent=3,
    calls_per_minute=30
)
```

### Job Processing Pipeline

```python
from backend.agents.job_description_graph import graph
from models.job_description_workflow_state import JobDescriptionProcessingState

# Process a job listing
state = JobDescriptionProcessingState(
    job_id="job_id",
    raw_job_data=job_data
)
result = await graph.ainvoke(state)
```

## Development

### Running Tests

```bash
# Run all tests
pytest backend/tests/

# Run specific test file
pytest backend/tests/test_extraction_graph.py
```

### Using Notebooks

The `backend/notebooks/` directory contains Jupyter notebooks for:
- Testing job search functionality (`google_talent.ipynb`)
- Developing resume parsing features (`Resume_Parser.ipynb`)

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
