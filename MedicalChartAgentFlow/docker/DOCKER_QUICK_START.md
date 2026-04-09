# 🐳 Docker Quick Start - 3 Minutes to Running

Get the Medical Chart Validation System running in Docker in just 3 minutes!

## ⚡ Prerequisites

- Docker Desktop installed and running
- 5GB free disk space

## 🚀 Three Commands to Success

### 1️⃣ Setup Environment (30 seconds)

```bash
# Copy environment template
cp .env.example .env

# Create data directory
mkdir data
```

### 2️⃣ Build and Start (2 minutes)

```bash
# Build and start containers
docker compose up -d
```

### 3️⃣ Access Application (instant)

Open browser: **http://localhost:8501**

## ✅ Verify It's Working

You should see:
- 🏥 Medical Chart Validation System interface
- 📋 Four tabs: Validate, Results, Dashboard, AI Insights
- Sample data available in dropdown

## 🧪 Test with Sample Data

1. Go to **"Validate"** tab
2. Select **"Use sample data"**
3. Choose **"chart_MBR001.txt"**
4. Keep **"Use bundled gap_report.csv"** checked
5. Click **"🚀 Run Validation"**
6. See results in ~5 seconds!

## 📊 View Results

- **Results Tab**: See validation history
- **Dashboard Tab**: View metrics and charts
- **AI Insights Tab**: Ask questions (requires Groq API key)

## 🛑 Stop Application

```bash
# Stop containers (keeps data)
docker compose down

# Stop and remove all data
docker compose down -v
```

## 🔧 Common Issues

### Port Already in Use
```bash
# Edit docker-compose.yml, change port:
ports:
  - "8080:8501"  # Use 8080 instead
```

### Container Won't Start
```bash
# Check logs
docker compose logs -f medchart-app

# Rebuild
docker compose up -d --build
```

### Database Issues
```bash
# Reset database
rm -rf data/
mkdir data
docker compose restart
```

## 📚 Need More Help?

- **Full Documentation**: See [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **Application Guide**: See [README.md](README.md)
- **Troubleshooting**: See [DOCKER_SETUP.md#troubleshooting](DOCKER_SETUP.md#troubleshooting)

## 🎯 What's Running?

```bash
# Check status
docker compose ps

# View logs
docker compose logs -f

# Resource usage
docker stats medchart-app
```

## 🎨 Architecture

```
┌─────────────────────────────────────┐
│   Browser (localhost:8501)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Docker Container: medchart-app    │
│   ┌─────────────────────────────┐   │
│   │  Streamlit Application      │   │
│   │  - 4 Agent Pipeline         │   │
│   │  - SQLite Database          │   │
│   │  - Sample Data              │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Host Volumes                      │
│   - ./data (database)               │
│   - ./sample_data (test files)      │
└─────────────────────────────────────┘
```

## 🚀 Next Steps

1. ✅ Run all 5 test cases (MBR001-MBR005)
2. ✅ Check Dashboard for metrics
3. ✅ Upload your own chart files
4. ✅ Add Groq API key for AI features
5. ✅ Explore production deployment

---

**That's it! You're running a containerized medical validation system! 🎉**