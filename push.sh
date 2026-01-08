#!/bin/bash

# Color codes for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Git Push with Submodules${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check for uncommitted changes in top-level repo
echo -e "${YELLOW}Checking for uncommitted changes...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Warning: You have uncommitted changes in the top-level repo${NC}"
    git status --short
    echo ""
fi

# Check submodule status
echo -e "${YELLOW}Checking submodule status...${NC}"
git submodule status --recursive
echo ""

# Show what will be pushed
echo -e "${YELLOW}Checking what will be pushed...${NC}"
git push --dry-run --recurse-submodules=on-demand 2>&1 | head -20
echo ""

# Ask for confirmation
read -p "Do you want to proceed with the push? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Push cancelled.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Pushing all repositories...${NC}"
echo ""

# Perform the actual push with recurse-submodules
git push --recurse-submodules=on-demand "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}  ✓ Push completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
else
    echo ""
    echo -e "${YELLOW}=====================================${NC}"
    echo -e "${YELLOW}  ✗ Push failed!${NC}"
    echo -e "${YELLOW}=====================================${NC}"
    exit 1
fi
