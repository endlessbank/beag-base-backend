# Beag Boilerplate Backend

A FastAPI backend for integrating with Beag.io subscription management system.

## Features

- 🚀 FastAPI with async support
- 📦 PostgreSQL database with SQLAlchemy ORM
- 🔄 Automatic subscription syncing every 6 hours
- 🔐 CORS configuration for frontend/admin access
- 📝 Auto-generated API documentation
- 🗄️ Automatic database setup for local development

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Beag.io account with API key

## Quick Start (Local Development)

### 1. Clone the repository

```bash
git clone <repository-url>
cd beag-base/backend
```

### 2. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 3. Configure environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Beag API key:
# BEAG_API_KEY=your_actual_api_key_here
```

### 4. Set up database

```bash
./setup-database.sh
```

This will:
- Create PostgreSQL user and database
- Provide you with the correct DATABASE_URL
- Guide you through database configuration

When prompted, you can:
- Press Enter to use defaults (database: `beag_db`, user: `beag_user`, password: `beag_password`)
- Or enter custom values to match your `.env` file

After setup, copy the generated DATABASE_URL to your `.env` file.

### 5. Run the backend

```bash
./start.sh
```

This will automatically:
- Check PostgreSQL installation
- Create virtual environment
- Install Python dependencies
- Run database migrations
- Start the API server with background worker

The backend will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Set up database
./setup-database.sh

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Users
- `POST /api/users/` - Create a new user
- `GET /api/users/` - List all users
- `GET /api/users/by-email/{email}` - Get user by email
- `POST /api/users/sync/{user_id}` - Manually sync user subscription

### Subscriptions
- `GET /api/subscriptions/check/{email}` - Check subscription (real-time from Beag)
- `GET /api/subscriptions/cached/{email}` - Get cached subscription data
- `POST /api/subscriptions/sync-all` - Manually sync all subscriptions

### Health & Monitoring
- `GET /health` - Basic health check
- `GET /api/health/frontend` - Frontend environment validation
- `GET /api/health/backend` - Backend environment validation

## How It Works

1. **User Creation**: When a user logs in via frontend, they're automatically created and synced
2. **Background Sync**: Every 6 hours, the worker syncs all users' subscriptions
3. **Caching**: Subscription data is stored locally for fast access
4. **Real-time Checks**: You can always check real-time subscription status via the API

## Database Schema

### Users Table
- `id` - Primary key
- `email` - User's email (unique)
- `beag_client_id` - Beag's internal client ID
- `subscription_status` - Current subscription status (PAID, CANCELLED, etc.)
- `plan_id` - Subscription plan ID
- `start_date` - Subscription start date
- `end_date` - Subscription end date
- `last_synced` - When the subscription was last synced
- `created_at` - User creation timestamp
- `updated_at` - Last update timestamp

### Sync Logs Table
- Tracks all sync operations
- Records success/failure and number of users synced

## Configuration

All configuration is done via environment variables in `.env`:

```env
# Beag.io Configuration (Required)
BEAG_API_KEY=your_beag_api_key_here
BEAG_API_URL=https://my-saas-basic-api-d5e3hpgdf0gnh2em.eastus-01.azurewebsites.net/api/v1/saas

# Database (Auto-created for local dev, using pg8000 for Python 3.13+ compatibility)
DATABASE_URL=postgresql+pg8000://beag_user:beag_password@localhost:5432/beag_db

# CORS Configuration
FRONTEND_URL=http://localhost:3000
ADMIN_URL=http://localhost:3001

# Server
PORT=8000
ENVIRONMENT=development

# Worker Configuration
SYNC_INTERVAL_HOURS=6  # How often to sync subscriptions
```

## Database Management

**Database Driver**: This backend uses `pg8000` (pure Python PostgreSQL driver) instead of `psycopg2` for better Python 3.13+ compatibility and deployment reliability.

### Running migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Database commands
```bash
# Access PostgreSQL CLI
psql -U beag_user -d beag_db

# Backup database
pg_dump -U beag_user beag_db > backup.sql

# Restore database
psql -U beag_user beag_db < backup.sql
```

## Production Deployment

### Important: Database Setup

**For production deployments, you must create the database through your hosting platform:**

### Platform-Specific Instructions

#### Railway
1. Add PostgreSQL plugin to your project
2. Railway automatically provides `DATABASE_URL`
3. Deploy your backend
4. Tables are created automatically on first run

#### Render
1. Create a PostgreSQL database in Render dashboard
2. Copy the External Database URL
3. Add as `DATABASE_URL` environment variable
4. Set the **Start Command** to:
   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. **Important**: Set Python version to 3.11 in environment variables
6. Deploy your backend
7. Tables are created automatically, background worker starts with the API

**Note**: A `render.yaml` configuration file is included for easy deployment

#### Heroku
1. Add Heroku Postgres addon
2. `DATABASE_URL` is set automatically
3. Deploy with git push
4. Tables are created on first run

#### AWS / Google Cloud / Azure
1. Create a managed PostgreSQL instance
2. Create a database within the instance
3. Configure security groups/firewall
4. Set `DATABASE_URL` in your deployment
5. Tables are created when backend starts

### Start Commands for Production

**Most platforms (Render, Railway, Heroku):**
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Docker containers:**
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Notes:**
- The command runs database migrations first (`alembic upgrade head`)
- Then starts the FastAPI server with built-in background worker
- Background worker automatically syncs subscriptions every `SYNC_INTERVAL_HOURS`
- Use `$PORT` for platforms that set the port automatically

### Environment Variables for Production

```env
# Required
BEAG_API_KEY=your_production_api_key
DATABASE_URL=postgresql://user:pass@host:port/dbname  # From your platform

# Update these for production
FRONTEND_URL=https://yourapp.com
ADMIN_URL=https://admin.yourapp.com
ENVIRONMENT=production

# Optional
PORT=8000  # Some platforms set this automatically
SYNC_INTERVAL_HOURS=6
```

### Deployment Checklist

- [ ] Database created through platform UI
- [ ] `DATABASE_URL` environment variable set
- [ ] `BEAG_API_KEY` environment variable set
- [ ] CORS origins updated for production URLs
- [ ] HTTPS enabled
- [ ] Monitoring/logging configured
- [ ] Backup strategy in place

## Development Tips

### Running tests
```bash
pytest
```

### Checking logs
```bash
# View sync logs
tail -f logs/sync.log  # If logging to file

# View database logs
psql -U beag_user -d beag_db -c "SELECT * FROM sync_logs ORDER BY created_at DESC LIMIT 10;"
```

### Common Issues

**Database connection errors:**
- Ensure PostgreSQL is running
- Check DATABASE_URL is correct
- Verify user has proper permissions

**CORS errors:**
- Update FRONTEND_URL and ADMIN_URL in .env
- Restart the server after changes

**Sync not working:**
- Check BEAG_API_KEY is valid
- Look for errors in console output
- Verify network connectivity

## License

MIT