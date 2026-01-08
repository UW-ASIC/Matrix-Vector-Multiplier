#!/bin/bash

# Color codes for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Commit & Push All (Recursive)${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Function to commit in a directory
commit_repo() {
    local dir=$1
    local name=$2
    
    cd "$dir"
    
    # Check if there are changes
    if git diff-index --quiet HEAD -- 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard)" ]; then
        echo -e "${GREEN}✓ No changes in $name${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}Changes detected in $name:${NC}"
    git status --short
    echo ""
    
    read -p "Commit message for $name: " commit_msg
    
    if [ -z "$commit_msg" ]; then
        echo -e "${RED}Commit cancelled (empty message)${NC}"
        return 1
    fi
    
    git add -A
    git commit -m "$commit_msg"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Committed in $name${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Failed to commit in $name${NC}"
        return 1
    fi
}

REPO_ROOT=$(pwd)

echo -e "${BLUE}STEP 1: Committing all changes${NC}"
echo ""

# Step 1: Commit in UWASIC-ALG (deepest submodule)
if [ -d "analog/library/tools/dep_library/UWASIC-ALG/.git" ]; then
    echo -e "${BLUE}[1/3] Checking UWASIC-ALG submodule...${NC}"
    commit_repo "$REPO_ROOT/analog/library/tools/dep_library/UWASIC-ALG" "UWASIC-ALG"
    cd "$REPO_ROOT"
fi

# Step 2: Commit in analog/library
if [ -d "analog/library/.git" ]; then
    echo -e "${BLUE}[2/3] Checking analog/library submodule...${NC}"
    commit_repo "$REPO_ROOT/analog/library" "analog/library"
    cd "$REPO_ROOT"
fi

# Step 3: Commit in top-level repo
echo -e "${BLUE}[3/3] Checking top-level repository...${NC}"
commit_repo "$REPO_ROOT" "Matrix-Vector-Analog (top-level)"

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  ✓ All commits complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Now push everything
echo -e "${BLUE}STEP 2: Pushing all repositories${NC}"
echo ""

# Check submodule status
echo -e "${YELLOW}Submodule status:${NC}"
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
