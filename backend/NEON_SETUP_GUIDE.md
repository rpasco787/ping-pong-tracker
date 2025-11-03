# Setting Up PostgreSQL with Neon for Deployment

This guide will walk you through setting up a PostgreSQL database on Neon for your Ping Pong Tracker app.

## Prerequisites

- Your backend code is already PostgreSQL-ready! ✅
- `psycopg2-binary` is already in requirements.txt ✅
- Your code uses `DATABASE_URL` environment variable ✅

---

## Step 1: Create a Neon Account and Database

### 1.1 Sign Up for Neon
1. Go to [https://neon.tech](https://neon.tech)
2. Click **Sign Up** (you can use GitHub, Google, or email)
3. Verify your email if required

### 1.2 Create Your First Project
1. After logging in, click **Create Project** (or it may create one automatically)
2. Set the following:
   - **Project Name**: `ping-pong-tracker` (or your preferred name)
   - **Region**: Choose the closest region to your users (e.g., `US East (Ohio)`)
   - **PostgreSQL Version**: Use the default (latest stable, usually 16 or 17)
3. Click **Create Project**

### 1.3 Get Your Connection String
After creation, you'll see a **Connection String**. It looks like this:
```
postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Important:** Copy this string and save it securely! You'll need it in the next steps.

---

## Step 2: Set Up Local Environment Configuration

### 2.1 Create `.env` File for Local Development

In your `backend/` directory, create a file called `.env`:

```bash
cd /Users/ryanpascual/Documents/repos/ping-pong-tracker-1/backend
touch .env
```

Add the following content to `.env`:

```env
# For local development (using SQLite)
DATABASE_URL=sqlite:///./ping_pong.db

# For testing with Neon PostgreSQL, uncomment and use your connection string:
# DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# JWT Secret Key
SECRET_KEY=xasdjf9a89d7fa89sfujoi32jfj
```

### 2.2 Add `.env` to `.gitignore`

Make sure your `.gitignore` includes:
```
backend/.env
```

This prevents accidentally committing secrets to version control.

---

## Step 3: Install Dependencies (If Not Already Done)

```bash
cd /Users/ryanpascual/Documents/repos/ping-pong-tracker-1/backend
pip install -r requirements.txt
```

This installs `psycopg2-binary` which is the PostgreSQL driver for Python.

---

## Step 4: Run Migrations on Your Neon Database

### 4.1 Update Your `.env` to Use Neon

Edit your `backend/.env` file and replace the `DATABASE_URL` with your Neon connection string:

```env
# Use your actual Neon connection string here
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

SECRET_KEY=xasdjf9a89d7fa89sfujoi32jfj
```

### 4.2 Load Environment Variables and Run Migrations

**Option A: Using environment variables directly (recommended for first test)**
```bash
cd /Users/ryanpascual/Documents/repos/ping-pong-tracker-1/backend

# Set the DATABASE_URL environment variable
export DATABASE_URL="postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Run all migrations
alembic upgrade head
```

**Option B: If you have python-dotenv installed**
Your Alembic is already configured to read from the `DATABASE_URL` environment variable set in your code, so simply run:
```bash
alembic upgrade head
```

### 4.3 Verify Migrations

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 6e20894e54a6, initial migration
INFO  [alembic.runtime.migration] Running upgrade 6e20894e54a6 -> 8fa43f0c0505, Add User table
INFO  [alembic.runtime.migration] Running upgrade 8fa43f0c0505 -> e7943b047909, Add authentication
...
```

If successful, your Neon database now has all the tables! 🎉

---

## Step 5: Test Your Setup

### 5.1 Start Your Backend with Neon

```bash
cd /Users/ryanpascual/Documents/repos/ping-pong-tracker-1/backend

# Make sure DATABASE_URL is set to your Neon connection string
export DATABASE_URL="postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Start the server
uvicorn app.main:app --reload
```

### 5.2 Test API Endpoints

Open your browser or use curl:

```bash
# Health check
curl http://localhost:8000/health

# Get players (should return empty array initially)
curl http://localhost:8000/players

# Get matches
curl http://localhost:8000/matches
```

All endpoints should work! You're now running on PostgreSQL! 🚀

---

## Step 6: Deploy to Production

### Option A: Deploy on Vercel (for Next.js + FastAPI)

**For Backend:**
1. In your Vercel project settings, add environment variables:
   - `DATABASE_URL`: Your Neon connection string
   - `SECRET_KEY`: A secure random string

2. Deploy your backend

**For Frontend:**
1. Set your backend API URL in environment variables
2. Deploy your frontend

### Option B: Deploy on Railway

1. Create a new Railway project
2. Connect your GitHub repository
3. Add environment variables in Railway dashboard:
   - `DATABASE_URL`: Your Neon connection string
   - `SECRET_KEY`: A secure random string
4. Railway will auto-deploy on push

### Option C: Deploy on Render

1. Create a new Web Service on Render
2. Connect your repository
3. Add environment variables:
   - `DATABASE_URL`: Your Neon connection string
   - `SECRET_KEY`: A secure random string
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Step 7: Switching Between SQLite (Local) and PostgreSQL (Production)

### For Local Development (SQLite)
```env
# In backend/.env
DATABASE_URL=sqlite:///./ping_pong.db
```

### For Production (Neon PostgreSQL)
```env
# In your hosting platform's environment variables
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

Your code automatically handles both! The `db.py` file checks if the URL starts with "sqlite" and adjusts accordingly.

---

## Troubleshooting

### Issue: "Could not connect to server"
- Check your internet connection
- Verify your Neon connection string is correct
- Ensure `?sslmode=require` is at the end of the connection string

### Issue: "Permission denied for database"
- Double-check your username and password in the connection string
- Make sure you copied the entire connection string from Neon

### Issue: "relation does not exist"
- You need to run migrations: `alembic upgrade head`
- Make sure `DATABASE_URL` is set when running migrations

### Issue: "SSL connection required"
- Add `?sslmode=require` to the end of your connection string

---

## Managing Your Neon Database

### View Your Database
1. Go to [console.neon.tech](https://console.neon.tech)
2. Select your project
3. Click **SQL Editor** to run queries
4. Or click **Tables** to browse your tables

### Monitor Usage
Neon free tier includes:
- 0.5 GB storage
- 100 hours of compute time per month
- Automatic database sleep after inactivity

### Backup Your Database
Neon automatically backs up your database. You can:
1. Create manual snapshots in the Neon console
2. Use `pg_dump` to create local backups:
```bash
pg_dump "postgresql://username:password@ep-xxx.neon.tech/neondb?sslmode=require" > backup.sql
```

---

## Next Steps

1. ✅ Test all your API endpoints with the Neon database
2. ✅ Deploy your backend to your hosting platform
3. ✅ Update your frontend API URL to point to the deployed backend
4. ✅ Test the full application end-to-end
5. ✅ Set up monitoring and error tracking (optional)

---

## Summary

You've successfully:
- ✅ Set up a Neon PostgreSQL database
- ✅ Configured your app to use PostgreSQL
- ✅ Run migrations on Neon
- ✅ Tested your setup locally

Your app is now production-ready with PostgreSQL! 🎉

**Need help?** Check the [Neon Documentation](https://neon.tech/docs) or open an issue in your repository.

