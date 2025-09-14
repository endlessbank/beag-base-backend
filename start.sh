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

# Parse database configuration from DATABASE_URL in .env
if ! grep -q "^DATABASE_URL=" .env; then
    echo "❌ DATABASE_URL not found in .env file!"
    echo ""
    echo "Please run ./setup-database.sh first to create your database."
    exit 1
fi

# Extract DATABASE_URL
DATABASE_URL=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2-)

# Parse DATABASE_URL to extract connection details
# Format: postgresql+pg8000://user:password@host:port/database
if [[ $DATABASE_URL =~ postgresql\+?[^:]*://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASSWORD="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo "❌ Invalid DATABASE_URL format in .env file!"
    echo "Expected format: postgresql+pg8000://user:password@host:port/database"
    echo "Current value: $DATABASE_URL"
    exit 1
fi

# Check if database exists and is accessible
echo "🗄️  Checking database connection..."
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
if ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q' 2>/dev/null; then
    echo "❌ Cannot connect to database!"
    echo ""
    echo "This might be because:"
    echo "1. Database doesn't exist - run ./setup-database.sh to create it"
    echo "2. PostgreSQL service isn't running - start it with 'brew services start postgresql@15'"
    echo "3. Wrong credentials in DATABASE_URL"
    echo ""
    echo "Current DATABASE_URL:"
    echo "$DATABASE_URL"
    exit 1
fi

echo "✅ Database connection successful!"

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