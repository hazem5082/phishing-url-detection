# Production Deployment Guide

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│  Client Application (Web, Mobile, CLI)              │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST
                     ▼
         ┌───────────────────────┐
         │  Flask REST API       │
         │  (app.py)             │
         │  Port: 5000           │
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │ Models │  │ Config  │  │ Dataset  │
   │(5 .pkl)│  │ (env)   │  │(.csv)    │
   └────────┘  └─────────┘  └──────────┘
```

## Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- **Kaggle API credentials** (for auto-download)
- **Docker** (optional, for containerized deployment)

## Local Development Setup

### 1. Clone and Install

```bash
git clone <repository>
cd phishing-url-detection
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env

# Edit .env with your settings
# Set KAGGLE_USERNAME and KAGGLE_KEY for auto-download
# Or setup ~/.kaggle/kaggle.json (recommended)
```

### 3. Get Kaggle Credentials

**Option A: Using kaggle.json (Recommended)**

```bash
# Visit: https://www.kaggle.com/settings/account
# Click "Create New API Token"
# This downloads kaggle.json

# On Windows:
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\

# On Linux/Mac:
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**Option B: Environment Variables**

```bash
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key
```

### 4. Initialize (First Time Only)

```bash
# Option 1: Automated initialization with startup script
python startup.py

# Option 2: Manual steps
# Step 1: Download dataset
python dataset_manager.py

# Step 2: Train models
python main.py --skip-eda

# Step 3: Start API
python app.py
```

### 5. Test the API

In another terminal:

```bash
# Health check
curl http://localhost:5000/health

# List models
curl http://localhost:5000/models

# Single prediction (bash)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [0.5, 0.3, 0.1, 0.2, 0.4, 0.6, 0.1, 0.3, 0.2, 0.5, 0.4, 0.3, 0.2, 0.1, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.5, 0.6, 0.4, 0.3, 0.2, 0.1, 0.5, 0.4, 0.3, 0.2, 0.1, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.5, 0.6, 0.4, 0.3, 0.2, 0.1, 0.5, 0.4, 0.3, 0.2, 0.1],
    "model": "XGBoost"
  }'
```

---

## Docker Deployment

### 1. Build and Run

```bash
# Build image
docker build -t phishing-detection:latest .

# Run container
docker run -p 5000:5000 \
  -e ENV=production \
  -e AUTO_DOWNLOAD_DATASET=true \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models_saved:/app/models_saved \
  phishing-detection:latest
```

### 2. Docker Compose (Recommended)

```bash
# Start services
docker-compose up --build

# In background
docker-compose up -d

# View logs
docker-compose logs -f phishing-api

# Stop services
docker-compose down
```

### 3. Environment Configuration in Docker

Create a `.env.prod` file:

```bash
ENV=production
LOG_LEVEL=INFO
AUTO_DOWNLOAD_DATASET=true
AUTO_TRAIN_MODELS=false
API_WORKERS=4
```

Pass it to docker-compose:

```bash
docker-compose --env-file .env.prod up --build
```

---

## Production Deployment (Cloud)

### AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. SSH into instance

ssh -i keypair.pem ubuntu@<public-ip>

# 3. Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose

# 4. Clone repository
git clone <repo>
cd phishing-url-detection

# 5. Configure environment
nano .env  # Set KAGGLE credentials

# 6. Start with Docker Compose
sudo docker-compose up -d

# 7. Setup nginx reverse proxy (optional)
# Configure nginx to forward :80 to :5000
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests:

```bash
# Deploy to k8s cluster
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=phishing-detection
kubectl logs <pod-name>
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Automatic (built-in to container)
# Configured in Dockerfile:
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3

# Manual check
curl http://localhost:5000/health
```

### Logs

```bash
# Local
python app.py 2>&1 | tee app.log

# Docker
docker-compose logs phishing-api
docker logs <container-id>
```

### Retraining Models

If you want to retrain models with new data:

```bash
# Set environment variable
export AUTO_TRAIN_MODELS=true

# Restart the application
docker-compose restart phishing-api
```

Or manually:

```bash
python main.py --skip-eda
```

---

## Performance Tuning

### API Workers

Increase for high-traffic scenarios:

```bash
# In .env
API_WORKERS=8  # More workers = more concurrent requests
```

### Model Selection

Different models have different performance characteristics:

- **XGBoost**: Fast, accurate (recommended)
- **Logistic Regression**: Very fast, good for real-time
- **Random Forest**: Balanced, good interpretability
- **MLP**: Slower, can be very accurate

Use `model` parameter in request to select:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [...], "model": "LogisticRegression"}'
```

---

## Troubleshooting

### Issue: "No models found"

```bash
# Ensure models are trained
python main.py --skip-eda

# Check models_saved/ directory
ls -la models_saved/
```

### Issue: Dataset download fails

```bash
# Check Kaggle credentials
cat ~/.kaggle/kaggle.json

# Manually download from Kaggle and place at:
# data/raw/phishing_dataset.csv
```

### Issue: API won't start

```bash
# Check if port 5000 is in use
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Use different port
API_PORT=8000 python app.py
```

### Issue: Out of memory

```bash
# Reduce batch size (if implementing)
# Or increase Docker memory limit:
docker-compose.yml:
  services:
    phishing-api:
      mem_limit: 2g
```

---

## Scaling Strategies

### Horizontal Scaling (Docker Swarm/Kubernetes)

```yaml
# docker-compose.yml
services:
  phishing-api:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

### Load Balancing

```nginx
# nginx config
upstream phishing_api {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}

server {
    listen 80;
    location / {
        proxy_pass http://phishing_api;
    }
}
```

---

## Security Best Practices

1. **Use HTTPS in production**
   - Terminate SSL at load balancer
   - Use certificates (Let's Encrypt)

2. **API Authentication**
   - Implement API key authentication
   - Use JWT tokens for client apps

3. **Rate Limiting**
   - Limit requests per IP/API key
   - Prevent abuse

4. **Input Validation**
   - Validate feature dimensions
   - Sanitize all inputs

5. **Secrets Management**
   - Never commit .env files
   - Use environment variables for credentials
   - Rotate Kaggle API keys periodically

---

## Backup & Disaster Recovery

```bash
# Backup trained models
tar czf models_backup_$(date +%Y%m%d).tar.gz models_saved/

# Backup dataset
tar czf data_backup_$(date +%Y%m%d).tar.gz data/

# Backup configurations
tar czf config_backup_$(date +%Y%m%d).tar.gz .env *.py
```

---

## Support & Documentation

- API Docs: See README.md for endpoint documentation
- Configuration: See .env.example for all options
- Code Structure: See project directory layout in README.md
- Issues: Open GitHub issue for bug reports

---

## Next Steps

1. ✓ Complete this deployment guide
2. Setup your deployment environment
3. Configure credentials and environment
4. Deploy using Docker Compose or manual steps
5. Monitor and maintain the system

Deployment complete!
