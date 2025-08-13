# EUR-Lex Trade Scraper Setup Guide

## Overview
This scraper uses **web scraping** to extract trade-related documents from EUR-Lex's Advanced Search interface. We switched from SOAP API due to authentication complexities.

## Required Credentials
You need EUR-Lex login credentials to access the advanced search features:

1. **Register at EUR-Lex**: https://eur-lex.europa.eu/content/help/data-reuse/webservice.html
2. **Get your credentials**: Username and password for EUR-Lex login
3. **Note**: These are NOT SOAP API credentials - they're for web access

## Environment Setup

### Option 1: .env File (Recommended for Local Development)
```bash
# Copy the example file
cp env.example .env

# Edit .env with your credentials
EURLEX_USERNAME=your_actual_username
EURLEX_PASSWORD=your_actual_password
```

### Option 2: Environment Variables
```bash
export EURLEX_USERNAME=your_actual_username
export EURLEX_PASSWORD=your_actual_password
```

## Why Web Scraping Instead of SOAP?
- **SOAP API**: Requires complex ECAS authentication that's difficult to automate
- **Web Scraping**: More reliable, easier to implement, and provides the same data
- **Result**: Same functionality, better reliability

## Testing Your Setup
```bash
# Test the web client connection
python3 test_web_client.py

# Test the full scraper
python3 run_scraper.py --test-connection
```
