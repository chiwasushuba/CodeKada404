# Render Deployment Guide

This guide walks you through deploying the Central Brain FastAPI backend to [Render](https://render.com).

## Prerequisites

- GitHub account with your repository
- Render account (free at https://render.com)
- All API keys ready (MongoDB URI, Pinecone, Google Gemini, AWS R2)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your code is pushed to GitHub:

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

**Important:** The `render.yaml` file is included in the repo and will auto-configure most settings.

### 2. Create a Render Account

Go to https://render.com and sign up (free tier available).

### 3. Connect Your GitHub Repository

1. Click **Dashboard** → **New +** → **Web Service**
2. Select **Build and deploy from a Git repository**
3. Click **Connect account** (GitHub)
4. Authorize Render to access your GitHub repositories
5. Select your `CodeKada404` repository
6. Choose the `main` branch

### 4. Configure the Service

When Render detects `render.yaml`, most settings will auto-populate. You can also configure manually:

**Name:**
```
central-brain-api
```

**Environment:**
```
Python
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python run.py
```

**Plan:**
```
Free (for testing) or Starter+ (for production)
```

### 5. Add Environment Variables

This is **critical**. Go to the **Environment** tab and add these variables:

#### Server Configuration:
```
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=info
ENVIRONMENT=production
DEBUG=false
RELOAD=false
```

#### Database & Services (Use the values from your .env):
```
MONGODB_URI=mongodb+srv://your-username:your-password@cluster.mongodb.net/central_brain?retryWrites=true&w=majority
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east1-aws
PINECONE_INDEX_NAME=codekada
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxx
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=https://account-id.r2.cloudflarestorage.com
AWS_REGION=us-east-1
```

#### CORS Configuration (Update with your frontend URL):
```
CORS_ORIGINS=["https://your-frontend.vercel.app", "https://your-domain.com"]
```

### 6. Deploy

Click **Create Web Service** and wait for Render to:

1. Install dependencies
2. Build the application
3. Start the server

You'll see a URL like: `https://central-brain-api-xxx.onrender.com`

## Verify Deployment

Once deployed, test these endpoints:

**Health Check:**
```bash
curl https://central-brain-api-xxx.onrender.com/health
```

**API Docs:**
```
https://central-brain-api-xxx.onrender.com/docs
```

**Root Endpoint:**
```bash
curl https://central-brain-api-xxx.onrender.com/
```

## Environment-Specific Settings

The `run.py` reads from `.env` or Render environment variables. These are automatically used:

| Variable | Local Dev | Production (Render) |
|----------|-----------|-------------------|
| `HOST` | `127.0.0.1` | `0.0.0.0` |
| `PORT` | `8000` | `8080` |
| `DEBUG` | `true` | `false` |
| `RELOAD` | `true` | `false` |
| `ENVIRONMENT` | `development` | `production` |

## Using render.yaml

If you want Render to auto-configure, the `render.yaml` file includes:

```yaml
startCommand: python run.py
buildCommand: pip install -r requirements.txt
envVars:
  - key: ENVIRONMENT
    value: production
  - key: HOST
    value: 0.0.0.0
```

Just add your secrets in the Render dashboard (they override the default values).

## Troubleshooting

### Build Fails

**Check logs:** Click **Logs** in the Render dashboard

**Common issues:**
- Missing `requirements.txt` dependencies
- Python version mismatch (Python 3.10+ required)
- GitHub credentials not connected properly

### Application Won't Start

Check the startup logs for errors. Common issues:

```
ModuleNotFoundError: No module named 'app'
```
→ Make sure you're in the `backend` directory when running

```
ERROR: Settings not found
```
→ Environment variables not set in Render dashboard

```
Connection refused on MongoDB
```
→ Check `MONGODB_URI` and IP whitelist in MongoDB Atlas

### Endpoints Return 404

- Make sure the service is fully deployed (green status)
- Check CORS settings in `CORS_ORIGINS`
- Verify the correct URL (including `/api/` prefix for routes)

### Performance Issues

Free tier Render instances sleep after 15 minutes of inactivity. Upgrade to **Starter+** for persistent service.

## Updating Your Deployment

To update your backend after making changes:

1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

2. Render automatically redeploys (if "Auto-Deploy" is enabled)

3. Check deployment status in Render dashboard → **Deployments**

## Custom Domain (Optional)

1. In Render dashboard, go to **Settings** → **Custom Domains**
2. Add your domain (e.g., `api.yourdomain.com`)
3. Follow DNS configuration instructions from your domain provider
4. HTTPS is automatically enabled via Let's Encrypt

## Environment Variables Best Practices

- **Never commit `.env` with real values to GitHub**
- Use Render's **Environment** tab for production secrets
- Mark sensitive variables as "Secret" in Render (optional)
- Rotate API keys regularly
- Keep a `.env.example` template in the repo for reference

## Connecting Frontend to Backend

Update your frontend's API base URL:

**Local development:**
```javascript
const API_BASE = "http://localhost:8000"
```

**Production (Render):**
```javascript
const API_BASE = "https://central-brain-api-xxx.onrender.com"
```

## Cost Considerations

- **Free Tier:** Limited to one web service, 0.5 GB RAM
- **Starter+:** $7/month, 0.5 GB RAM, no auto-sleep
- **Standard:** $25/month, 1 GB RAM, load balancing

For hackathon testing, the free tier is sufficient!

## Support & Resources

- [Render Docs](https://render.com/docs)
- [Render Dashboard](https://dashboard.render.com)
- [Contact Render Support](https://support.render.com)

---

**Need help?** Check the [main README](./README.md) for local development setup.
