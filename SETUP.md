# AiRoHire Setup Guide

Complete setup instructions for the AiRoHire video call participant management system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Manual Setup](#manual-setup)
- [Development Environment](#development-environment)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker & Docker Compose** (recommended)
  - Docker Engine 20.10+
  - Docker Compose 2.0+

**OR for manual setup:**

- **Node.js** 18.x or higher
- **Python** 3.11 or higher
- **PostgreSQL** 15 or higher

### System Requirements

- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space
- **OS:** Linux, macOS, or Windows with WSL2

## Quick Start with Docker

The fastest way to get AiRoHire running is with Docker:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd video-call-assignment
```

### 2. Run the Setup Script

```bash
# Make the script executable
chmod +x docker-setup.sh

# Run interactive setup
./docker-setup.sh
```

### 3. Choose Your Mode

The setup script will prompt you to choose:

1. **Development** (with hot reload)
2. **Production** (optimized build)
3. **Clean setup** (remove existing data)
4. **Show status** only
5. **Show logs**
6. **Stop** all services

### 4. Access the Application

Once setup is complete:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Database:** localhost:5432

### Quick Commands

```bash
# Production mode
./docker-setup.sh --prod

# Development mode
./docker-setup.sh --dev

# Clean setup (removes all data)
./docker-setup.sh --clean

# Check service status
./docker-setup.sh --status

# View logs
./docker-setup.sh --logs

# Stop all services
./docker-setup.sh --stop
```

## Manual Setup

If you prefer not to use Docker:

### 1. Database Setup

#### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from [PostgreSQL official site](https://www.postgresql.org/download/windows/)

#### Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE video_call_app;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE video_call_app TO postgres;
\q
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend/

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/video_call_app"

# Create database tables
python create_tables.py

# Seed initial data
python seed_data.py

# Start the backend server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in new terminal)
cd frontend/

# Install dependencies
npm install

# Set environment variables
export VITE_API_URL="http://localhost:8000"

# Start the development server
npm run dev
```

### 4. Access the Application

- **Frontend:** http://localhost:5173 (or the port shown in terminal)
- **Backend:** http://localhost:8000

## Development Environment

### Hot Reload Setup

**Backend:**
```bash
cd backend/
source .venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
cd frontend/
npm run dev
```

### Development with Docker

```bash
# Use development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Or use the setup script
./docker-setup.sh --dev
```

### Environment Files

For development, copy and modify:

```bash
cp .env.development .env
```

Edit the `.env` file with your local settings.

## Production Deployment

### Using Docker (Recommended)

```bash
# Production mode
./docker-setup.sh --prod

# Or manually with docker-compose
cp .env.production .env
docker-compose up --build -d
```

### Manual Production Setup

#### Backend Production

```bash
cd backend/

# Install production dependencies
pip install -r requirements.txt

# Set production environment variables
export DATABASE_URL="postgresql://user:password@host:5432/database"
export LOG_LEVEL="INFO"

# Create tables and seed data
python create_tables.py
python seed_data.py

# Start with production server (e.g., Gunicorn)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend Production

```bash
cd frontend/

# Install dependencies
npm ci --only=production

# Build for production
npm run build

# Serve with a static file server
npm install -g serve
serve -s dist -l 3000
```

### Nginx Configuration

For production, use the provided `nginx.conf`:

```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/airohire
sudo ln -s /etc/nginx/sites-available/airohire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Variables

### Backend Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `API_HOST` | API host binding | `0.0.0.0` | No |
| `API_PORT` | API port | `8000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | No |

### Frontend Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` | Yes |
| `NODE_ENV` | Environment mode | `development` | No |

### Setting Environment Variables

**Development:**
```bash
# Copy development template
cp .env.development .env

# Edit as needed
nano .env
```

**Production:**
```bash
# Copy production template  
cp .env.production .env

# Update with production values
nano .env
```

## Database Setup

### Schema Creation

The database schema is automatically created by running:

```bash
cd backend/
python create_tables.py
```

### Sample Data

Populate with sample participants:

```bash
cd backend/
python seed_data.py
```

### Database Migration

For schema changes, update the models in `models.py` and run:

```bash
# Drop and recreate (development only)
python create_tables.py

# For production, implement proper migrations
```

### Backup and Restore

**Backup:**
```bash
pg_dump -h localhost -U postgres video_call_app > backup.sql
```

**Restore:**
```bash
psql -h localhost -U postgres video_call_app < backup.sql
```

## Testing

### Running Tests

**Frontend Tests:**
```bash
cd frontend/
npm install
npm run test
```

**Backend Tests:**
```bash
cd backend/
pip install -r requirements.txt
python -m pytest tests/ -v
```

**All Tests:**
```bash
# Use the comprehensive test runner
./run_all_tests.sh
```

### Test Coverage

**Frontend:**
```bash
npm run test:coverage
```

**Backend:**
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

### Continuous Testing

**Frontend (watch mode):**
```bash
npm run test -- --watch
```

**Backend (with file watching):**
```bash
pip install pytest-watch
ptw
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Check what's using the port
lsof -ti:8000
lsof -ti:3000
lsof -ti:5173

# Kill the process
kill -9 <PID>

# Or use the provided script
./docker-setup.sh --stop
```

#### Database Connection Issues

1. **Check PostgreSQL is running:**
   ```bash
   sudo systemctl status postgresql
   # or
   brew services list | grep postgres
   ```

2. **Verify connection string:**
   ```bash
   # Test connection
   psql "postgresql://postgres:postgres@localhost:5432/video_call_app"
   ```

3. **Check firewall/permissions:**
   ```bash
   sudo ufw status
   ```

#### Docker Issues

1. **Docker not running:**
   ```bash
   sudo systemctl start docker
   # or
   open Docker Desktop
   ```

2. **Permission denied:**
   ```bash
   sudo usermod -aG docker $USER
   # Then log out and back in
   ```

3. **Clear Docker cache:**
   ```bash
   docker system prune -a
   docker volume prune
   ```

#### Frontend Build Issues

1. **Clear npm cache:**
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Node version issues:**
   ```bash
   # Check version
   node --version
   
   # Use nvm if needed
   nvm use 18
   ```

#### Backend Import Issues

1. **Python path issues:**
   ```bash
   export PYTHONPATH=/path/to/backend:$PYTHONPATH
   ```

2. **Virtual environment:**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   which python
   ```

### Log Files

**Docker logs:**
```bash
docker-compose logs -f [service_name]
```

**Application logs:**
- Backend: Check console output or `/app/logs/` in container
- Frontend: Check browser console for client-side errors

### Performance Issues

1. **Database performance:**
   ```sql
   -- Check slow queries
   SELECT query, mean_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC;
   ```

2. **Memory usage:**
   ```bash
   # Check container memory usage
   docker stats
   
   # Check system memory
   free -h
   ```

### Getting Help

1. **Check logs first:**
   ```bash
   ./docker-setup.sh --logs
   ```

2. **Verify service status:**
   ```bash
   ./docker-setup.sh --status
   ```

3. **Test API endpoints:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/participants
   ```

4. **Check network connectivity:**
   ```bash
   # From frontend container to backend
   docker exec airohire_frontend ping airohire_backend
   ```

## Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Testing Documentation:** [TESTING.md](TESTING.md)
- **Project README:** [README.md](README.md)

## Support

For issues not covered in this guide:

1. Check the project's issue tracker
2. Review log files for error messages
3. Ensure all prerequisites are met
4. Try a clean setup with `./docker-setup.sh --clean`

---

**Note:** This setup guide assumes a Unix-like environment. Windows users should use WSL2 or adapt commands accordingly.