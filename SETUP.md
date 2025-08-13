# 🇪🇺 EUR-Lex Trade Scraper - Setup Guide

## 📋 Quick Start

### 1. 🔑 Get EUR-Lex Credentials

1. **Register for EUR-Lex SOAP webservice** (free):
   - Visit: https://eur-lex.europa.eu/content/help/data-reuse/webservice.html
   - Fill out the registration form
   - Wait for email with your credentials (usually within 24 hours)

### 2. 🔧 Configure Credentials

You have **3 options** to set your EUR-Lex credentials:

#### Option A: Environment File (.env) - **RECOMMENDED**
```bash
# Copy the example file
cp env.example .env

# Edit the .env file with your credentials
nano .env
```

Edit `.env`:
```bash
EURLEX_USERNAME=your_actual_username
EURLEX_PASSWORD=your_actual_password
```

#### Option B: Export Environment Variables
```bash
export EURLEX_USERNAME='your_actual_username'
export EURLEX_PASSWORD='your_actual_password'
```

#### Option C: Shell Profile (Permanent)
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export EURLEX_USERNAME='your_actual_username'
export EURLEX_PASSWORD='your_actual_password'
```
Then reload: `source ~/.bashrc` or `source ~/.zshrc`

### 3. 🧪 Test Your Setup

```bash
# Test connection to EUR-Lex
python3 run_scraper.py --test-connection

# If successful, run a test scrape
python3 run_scraper.py --force-full-2024
```

### 4. 🌐 Start Web Dashboard

```bash
# Start the web server
python3 run_web.py

# Open in browser
open http://localhost:8000
```

## 🔍 Troubleshooting

### ❌ "EUR-Lex credentials not provided"
- Check your `.env` file exists and has the right format
- Verify environment variables: `echo $EURLEX_USERNAME`
- Make sure no extra spaces around the `=` sign

### ❌ "SOAP client not initialized"
- Install zeep: `pip3 install zeep`
- Check internet connection
- Verify WSDL URL is accessible

### ❌ "Authentication failed" 
- Double-check your username/password
- Make sure credentials are active (not expired)
- Contact EUR-Lex support if needed

### ❌ "No documents found"
- This is normal if no matching documents exist in the date range
- Try expanding the date range: `--force-full-2024`
- Check the keyword matching criteria in the logs

## 📁 File Structure

```
eurlex-trade-scraper/
├── .env                    # Your credentials (create this)
├── env.example            # Template for credentials
├── data/                  # Scraped data storage
│   ├── results-2025.json  # Matched documents
│   └── state.json         # Scraper state
├── src/                   # Source code
└── static/                # Web dashboard files
```

## 🚀 Deployment

### Vercel Deployment
```bash
# Set environment variables in Vercel dashboard
vercel env add EURLEX_USERNAME
vercel env add EURLEX_PASSWORD

# Deploy
vercel --prod
```

### Local Production
```bash
# Set production environment
export VERCEL_ENV=production

# Run with gunicorn (install: pip install gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

## 🔐 Security Notes

- **Never commit `.env` files** to git (already in `.gitignore`)
- Use environment variables in production
- Rotate credentials periodically
- Keep backups of your data directory

## 📞 Support

- **EUR-Lex API Issues**: Contact EUR-Lex webservice support
- **Application Issues**: Check the logs in terminal
- **Keyword Matching**: Review `src/matcher.py` for criteria

## 🎯 Keyword Criteria

The scraper uses **strict AND logic** across 3 groups:

1. **Trade Measures**: antidumping, countervailing duty, CVD, safeguard, etc.
2. **Products**: phosphate, fertilizer, DAP, MAP, TSP, etc.  
3. **Entities**: Morocco, OCP, Mosaic, Nutrien, Yara, etc.

**All 3 groups must match** for a document to be included.
