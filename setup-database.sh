#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗄️  PostgreSQL Database Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not installed!${NC}"
    echo ""
    echo "Please install PostgreSQL first:"
    echo -e "${YELLOW}  Mac:${NC} brew install postgresql@15"
    echo -e "${YELLOW}  Ubuntu:${NC} sudo apt install postgresql"
    echo -e "${YELLOW}  Windows:${NC} Download from https://www.postgresql.org/download/windows/"
    echo ""
    echo "After installing, run this script again."
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL is installed!${NC}"
echo ""

# Auto-detect PostgreSQL user
echo "Detecting PostgreSQL configuration..."
PG_USER=""

# Try to get the user from psql -l output
if psql -l &>/dev/null; then
    # User can connect without specifying username (macOS default)
    PG_USER=$(whoami)
elif psql -U postgres -l &>/dev/null; then
    # Standard postgres user exists
    PG_USER="postgres"
elif psql -U $(whoami) -l &>/dev/null; then
    # Current user works
    PG_USER=$(whoami)
else
    echo -e "${RED}❌ Could not connect to PostgreSQL${NC}"
    echo "Please make sure PostgreSQL is running."
    echo ""
    echo "Try starting it with:"
    echo -e "${YELLOW}  Mac:${NC} brew services start postgresql@15"
    echo -e "${YELLOW}  Ubuntu:${NC} sudo systemctl start postgresql"
    exit 1
fi

echo -e "${GREEN}✅ Connected to PostgreSQL as user: $PG_USER${NC}"
echo ""

# Get database name from user
echo -e "${BLUE}What would you like to name your database?${NC}"
echo -e "${YELLOW}(Use a unique name for each project)${NC}"
echo ""
read -p "Enter database name [beag_db]: " DB_NAME
DB_NAME="${DB_NAME:-beag_db}"

# Validate database name (alphanumeric and underscores only)
if [[ ! "$DB_NAME" =~ ^[a-zA-Z0-9_]+$ ]]; then
    echo -e "${RED}❌ Invalid database name!${NC}"
    echo "Please use only letters, numbers, and underscores."
    exit 1
fi

# Create user name based on database name
DB_USER="${DB_NAME}_user"

# Generate a secure password
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-16)

# Database connection details
DB_HOST="localhost"
DB_PORT="5432"

echo ""
echo -e "${BLUE}Creating database '${DB_NAME}'...${NC}"

# Check if database already exists
if psql -U $PG_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}⚠️  Database '$DB_NAME' already exists!${NC}"
    echo ""
    echo "Would you like to:"
    echo "1) Use the existing database"
    echo "2) Delete and recreate it"
    echo "3) Choose a different name"
    echo ""
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            echo -e "${GREEN}Using existing database '$DB_NAME'${NC}"
            # Try to get existing user password (this is a limitation - we can't retrieve it)
            echo -e "${YELLOW}Note: Using existing database. Make sure your .env has the correct password.${NC}"
            ;;
        2)
            echo "Dropping existing database..."
            psql -U $PG_USER <<EOF
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;
EOF
            ;;
        3)
            echo "Please run the script again with a different database name."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
fi

# Create database and user
if [ "$choice" != "1" ]; then
    # First, connect to postgres database for user creation
    psql -U $PG_USER -d postgres <<EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database created successfully!${NC}"
    else
        echo -e "${RED}❌ Database creation failed!${NC}"
        echo "Error details might be hidden. Try running the script again."
        exit 1
    fi
fi

# Update .env file
DATABASE_URL="postgresql+pg8000://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
ENV_FILE="$(dirname "$0")/.env"

echo ""
echo -e "${BLUE}Updating your .env file...${NC}"

if [ -f "$ENV_FILE" ]; then
    # Backup existing .env
    cp "$ENV_FILE" "$ENV_FILE.backup"
    
    # Update DATABASE_URL in .env
    if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
        # On macOS, sed requires '' after -i
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|" "$ENV_FILE"
        else
            sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|" "$ENV_FILE"
        fi
    else
        # Add DATABASE_URL if it doesn't exist
        echo "DATABASE_URL=$DATABASE_URL" >> "$ENV_FILE"
    fi
    
    echo -e "${GREEN}✅ Updated .env file with new DATABASE_URL${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found. Creating one...${NC}"
    cp "$(dirname "$0")/.env.example" "$ENV_FILE" 2>/dev/null || touch "$ENV_FILE"
    
    # Update or add DATABASE_URL
    if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|" "$ENV_FILE"
        else
            sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|" "$ENV_FILE"
        fi
    else
        echo "DATABASE_URL=$DATABASE_URL" >> "$ENV_FILE"
    fi
fi

echo ""
echo -e "${GREEN}🎉 All done! Your database is ready.${NC}"
echo ""
echo -e "${BLUE}Database Details:${NC}"
echo -e "  Database: ${YELLOW}$DB_NAME${NC}"
echo -e "  User:     ${YELLOW}$DB_USER${NC}"
echo -e "  Password: ${YELLOW}$DB_PASSWORD${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Make sure to add your BEAG_API_KEY to .env"
echo "2. Run: ./start.sh"
echo ""