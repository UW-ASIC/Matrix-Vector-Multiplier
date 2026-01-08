#!/bin/bash

# Color codes for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Git Pull with Submodules${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check for uncommitted changes in top-level repo
echo -e "${YELLOW}Checking for uncommitted changes...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Warning: You have uncommitted changes in the top-level repo${NC}"
    git status --short
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Pull cancelled.${NC}"
        exit 1
    fi
    echo ""
fi

# Pull the top-level repository
echo -e "${GREEN}Pulling top-level repository...${NC}"
git pull "$@"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Failed to pull top-level repository${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Updating submodules...${NC}"

# Initialize and update all submodules recursively
git submodule update --init --recursive --remote

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}  ✓ Pull completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "${BLUE}Submodule status:${NC}"
    git submodule status --recursive
else
    echo ""
    echo -e "${YELLOW}=====================================${NC}"
    echo -e "${YELLOW}  ✗ Submodule update failed!${NC}"
    echo -e "${YELLOW}=====================================${NC}"
    exit 1
fi
