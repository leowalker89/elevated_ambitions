#!/bin/bash
docker compose run --rm elevate-jobs 2>&1 | tee elevation_workflow.log 