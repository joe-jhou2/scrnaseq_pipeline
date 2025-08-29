#!/bin/bash
# This script sets up a PostgreSQL database in a Docker container for storing single-cell RNA-seq metadata.
docker compose -f "$(dirname "$0")/docker-compose.yml" up -d --build

echo "PostgreSQL database setup complete."