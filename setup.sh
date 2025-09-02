#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
poetry install

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
poetry run python manage.py migrate

# Create default admin account
echo -e "${YELLOW}Creating default admin account...${NC}"
poetry run python manage.py createadmin

echo -e "${GREEN}Setup complete.${NC}"