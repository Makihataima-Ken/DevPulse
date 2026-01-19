#!/bin/bash

# Default parameters
BASE_URL="${1:-http://localhost:8000}"
EMAIL="${2:-test@devpulse.com}"
PASSWORD="${3:-password123}"

# Color codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Function to print section headers
write_section() {
    local title=$1
    echo ""
    echo -e "${CYAN}${title}${NC}"
    printf "${GRAY}%${#title}s${NC}\n" | tr ' ' '-'
}

echo -e "${GREEN}DevPulse Full API Test Started${NC}"

# ============================
# 1. LOGIN
# ============================
write_section "[1/7] Login"

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

if [ $? -eq 0 ]; then
    ID_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"id_token":"[^"]*' | sed 's/"id_token":"//')
    UID=$(echo "$LOGIN_RESPONSE" | grep -o '"uid":"[^"]*' | sed 's/"uid":"//')
    
    if [ -n "$ID_TOKEN" ]; then
        echo -e "${GREEN}Login OK${NC}"
        echo "UID: $UID"
    else
        echo -e "${RED}Login Failed${NC}"
        echo "$LOGIN_RESPONSE"
        exit 1
    fi
else
    echo -e "${RED}Login Failed${NC}"
    exit 1
fi

# ============================
# 2. TEST AUTH
# ============================
write_section "[2/7] Test Auth"

AUTH_RESPONSE=$(curl -s -X GET "$BASE_URL/test-auth/" \
    -H "Authorization: Bearer $ID_TOKEN" \
    -H "Content-Type: application/json")

if [ $? -eq 0 ]; then
    FIREBASE_UID=$(echo "$AUTH_RESPONSE" | grep -o '"firebase_uid":"[^"]*' | sed 's/"firebase_uid":"//')
    if [ -n "$FIREBASE_UID" ]; then
        echo -e "${GREEN}Auth OK - UID: $FIREBASE_UID${NC}"
    else
        echo -e "${RED}Auth Test Failed${NC}"
        echo "$AUTH_RESPONSE"
    fi
else
    echo -e "${RED}Auth Test Failed${NC}"
fi

# ============================
# 3. CREATE ACTIVITY
# ============================
write_section "[3/7] Create Activity"

CURRENT_DATE=$(date +%Y-%m-%d)

CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/activities/" \
    -H "Authorization: Bearer $ID_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"date\":\"$CURRENT_DATE\",\"activity_type\":\"coding\"}")

if [ $? -eq 0 ]; then
    if echo "$CREATE_RESPONSE" | grep -q '"id"'; then
        echo -e "${GREEN}Activity Created${NC}"
    else
        echo -e "${RED}Create Activity Failed${NC}"
        echo "$CREATE_RESPONSE"
    fi
else
    echo -e "${RED}Create Activity Failed${NC}"
fi

# ============================
# 4. LIST ACTIVITIES
# ============================
write_section "[4/7] List Activities"

LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/api/activities/" \
    -H "Authorization: Bearer $ID_TOKEN" \
    -H "Content-Type: application/json")

if [ $? -eq 0 ]; then
    # Count activities (simple array count)
    COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id":' | wc -l)
    echo -e "${GREEN}Activities Count: $COUNT${NC}"
else
    echo -e "${RED}List Activities Failed${NC}"
fi

# ============================
# 5. STREAK
# ============================
write_section "[5/7] Get Streak"

STREAK_RESPONSE=$(curl -s -X GET "$BASE_URL/api/streak/" \
    -H "Authorization: Bearer $ID_TOKEN" \
    -H "Content-Type: application/json")

if [ $? -eq 0 ]; then
    CURRENT_STREAK=$(echo "$STREAK_RESPONSE" | grep -o '"current_streak":[0-9]*' | sed 's/"current_streak"://')
    LONGEST_STREAK=$(echo "$STREAK_RESPONSE" | grep -o '"longest_streak":[0-9]*' | sed 's/"longest_streak"://')
    
    echo "Current Streak: $CURRENT_STREAK"
    echo "Longest Streak: $LONGEST_STREAK"
else
    echo -e "${RED}Streak Failed${NC}"
fi

# ============================
# 6. GITHUB SYNC
# ============================
write_section "[6/7] GitHub Sync"

GITHUB_SYNC_RESPONSE=$(curl -s -X POST "$BASE_URL/api/github/sync/" \
    -H "Authorization: Bearer $ID_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"github_username":"Makihataima-Ken"}')

if [ $? -eq 0 ] && echo "$GITHUB_SYNC_RESPONSE" | grep -q '"message"'; then
    echo -e "${GREEN}GitHub Sync OK${NC}"
else
    echo -e "${YELLOW}GitHub Sync Failed (non-critical)${NC}"
fi

# ============================
# 7. GITHUB STATS
# ============================
write_section "[7/7] GitHub Stats"

GITHUB_STATS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/github/stats/?github_username=Makihataima-Ken" \
    -H "Authorization: Bearer $ID_TOKEN" \
    -H "Content-Type: application/json")

if [ $? -eq 0 ] && echo "$GITHUB_STATS_RESPONSE" | grep -q '"github_username"'; then
    echo -e "${GREEN}GitHub Stats OK${NC}"
else
    echo -e "${YELLOW}GitHub Stats Failed (non-critical)${NC}"
fi

echo ""
echo -e "${GREEN}ALL TESTS COMPLETED${NC}"