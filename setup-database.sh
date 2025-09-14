#!/bin/bash

echo "🗄️  Setting up PostgreSQL Database..."
echo ""

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed!"
    echo ""
    echo "Please install PostgreSQL first:"
    echo "  Mac: brew install postgresql@15"
    echo "  Ubuntu: sudo apt install postgresql"
    echo "  Windows: Download from https://www.postgresql.org/download/windows/"
    exit 1
fi

# Default values
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="beag_db"
DB_USER="beag_user"
DB_PASSWORD="beag_password"

echo "Enter database configuration (press Enter for defaults):"
read -p "Database host [$DB_HOST]: " input_host
read -p "Database port [$DB_PORT]: " input_port
read -p "Database name [$DB_NAME]: " input_name
read -p "Database user [$DB_USER]: " input_user
read -sp "Database password [$DB_PASSWORD]: " input_password
echo ""

# Use input values or defaults
DB_HOST="${input_host:-$DB_HOST}"
DB_PORT="${input_port:-$DB_PORT}"
DB_NAME="${input_name:-$DB_NAME}"
DB_USER="${input_user:-$DB_USER}"
DB_PASSWORD="${input_password:-$DB_PASSWORD}"

# Create database and user
echo ""
echo "Creating database and user..."
echo "You may need to enter your PostgreSQL superuser password:"

# Create user and database
psql -h $DB_HOST -p $DB_PORT -U postgres <<EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database created successfully!"
    echo ""
    echo "Your DATABASE_URL is:"
    echo "postgresql+pg8000://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    echo ""
    echo "Add this to your backend/.env file"
else
    echo "❌ Database creation failed!"
    echo "Please check your PostgreSQL installation and try again."
fi