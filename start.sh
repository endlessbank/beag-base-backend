#!/bin/bash

echo "🚀 Starting Backend API with Background Worker..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed!"
    echo ""
    echo "Please install PostgreSQL first:"
    echo "  Mac: brew install postgresql@15"
    echo "  Ubuntu: sudo apt install postgresql"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    cp .env.example .env
fi

# Check if BEAG_API_KEY is configured
if grep -q "BEAG_API_KEY=your_beag_api_key_here" .env || ! grep -q "BEAG_API_KEY=." .env; then
    echo "❌ BEAG_API_KEY not configured!"
    echo ""
    echo "Please edit .env and add your Beag API key:"
    echo "  BEAG_API_KEY=your_actual_api_key_here"
    echo ""
    echo "You can get your API key from your Beag.io dashboard."
    exit 1
fi

# Database configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="beag_db"
DB_USER="beag_user"
DB_PASSWORD="beag_password"

# Check if database exists, create if it doesn't
echo "🗄️  Checking database..."
if ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q' 2>/dev/null; then
    echo "📦 Database not found. Creating database..."
    
    # Try to create user and database
    psql -h $DB_HOST -p $DB_PORT -U postgres <<EOF 2>/dev/null
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

    if [ $? -eq 0 ]; then
        echo "✅ Database created successfully!"
    else
        echo "⚠️  Could not create database automatically."
        echo "Please run ./setup-database.sh first or create the database manually."
        echo ""
        echo "Expected DATABASE_URL:"
        echo "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
        exit 1
    fi
fi

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start the API server with integrated worker
echo "✅ Starting FastAPI server with background worker..."
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - Health: http://localhost:8000/health"
echo "   - Manual Sync: POST http://localhost:8000/sync-now"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload