"""
Vercel serverless function for the EUR-Lex Trade Scraper FastAPI app.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import EURLexTradeScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine data directory based on environment
if os.environ.get('VERCEL_ENV'):
    # Vercel deployment - use /tmp/data (temporary, but only option)
    DATA_DIR = os.environ.get('DATA_DIR', '/tmp/data')
    logger.info(f"Running on Vercel - using temporary data directory: {DATA_DIR}")
else:
    # Local development - use project data folder
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    logger.info(f"Running locally - using project data directory: {DATA_DIR}")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Initialize FastAPI app
app = FastAPI(
    title="EUR-Lex Trade Scraper API",
    description="API for scraping and analyzing EUR-Lex trade documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components with error handling
scraper = None
matcher = None

try:
    from src.matcher import EURLexTradeDocumentMatcher
    scraper = EURLexTradeScraper(data_dir=DATA_DIR)
    matcher = EURLexTradeDocumentMatcher()
    logger.info("Successfully imported scraper modules")
except ImportError as e:
    logger.error(f"Failed to import scraper modules: {e}")
    # Create mock objects for basic functionality
    class MockScraper:
        def _load_results(self): return []
        def get_statistics(self): return {"total_documents": 0, "last_run": None}
        def scrape(self, **kwargs): return {"status": "error", "message": "Scraper not available"}
        def export_csv(self, filters=None): return "No data available"
        def _apply_filters(self, results, filters): return results
        def test_connection(self): return {"status": "error", "message": "SOAP client not available"}
    
    class MockMatcher:
        measure_keywords = []
        product_keywords = []
        place_company_keywords = []
        def get_keyword_stats(self): return {}
    
    scraper = MockScraper()
    matcher = MockMatcher()

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main dashboard HTML."""
    try:
        # Try to read from static directory
        static_html = Path("/var/task/static/index.html")
        if static_html.exists():
            with open(static_html, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        
        # Fallback HTML
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>EUR-Lex Trade Scraper Dashboard</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/core@latest/dist/css/tabler.min.css">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="text-center">
                        <h1>🇪🇺 EUR-Lex Trade Scraper Dashboard</h1>
                        <p class="lead">European Union Trade Document Analyzer</p>
                        <div class="mt-4">
                            <a href="/api/health" class="btn btn-primary me-2">Health Check</a>
                            <a href="/docs" class="btn btn-outline-primary">API Documentation</a>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """)
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return HTMLResponse(content=f"<h1>Error loading dashboard: {str(e)}</h1>")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "EUR-Lex Trade Scraper", 
        "platform": "Vercel",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "data_dir": DATA_DIR,
        "scraper_available": scraper is not None and hasattr(scraper, '_load_results')
    }

@app.get("/api/dashboard-data")
async def get_dashboard_data(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(100)
):
    """Get filtered dashboard data."""
    try:
        if not scraper:
            return {"results": [], "statistics": {"total_documents": 0}, "filters_applied": {}, "total_returned": 0}
        
        # Build filters
        filters = {}
        if start_date: filters['start_date'] = start_date
        if end_date: filters['end_date'] = end_date
        if author: filters['author'] = author
        if company: filters['company'] = company
        if product: filters['product'] = product
        if search: filters['search'] = search
        
        # Debug logging
        logger.info(f"Dashboard data request - scraper data_dir: {scraper.data_dir}")
        logger.info(f"Dashboard data request - results_file: {scraper.results_file}")
        logger.info(f"Dashboard data request - results_file exists: {os.path.exists(scraper.results_file)}")
        
        # Get results
        results = scraper._load_results()
        logger.info(f"Dashboard data request - loaded {len(results)} results")
        
        if filters and hasattr(scraper, '_apply_filters'):
            results = scraper._apply_filters(results, filters)
        
        if limit and limit > 0:
            results = results[:limit]
        
        stats = scraper.get_statistics()
        
        return {
            "results": results,
            "statistics": stats,
            "filters_applied": filters,
            "total_returned": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {"results": [], "statistics": {"error": str(e)}, "filters_applied": {}, "total_returned": 0}

@app.get("/api/statistics")
async def get_statistics():
    """Get overall statistics."""
    try:
        if not scraper:
            return {"total_documents": 0, "last_run": None, "error": "Scraper not available"}
        return scraper.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {"error": str(e)}

@app.get("/api/keywords")
async def get_keywords():
    """Get keyword information."""
    try:
        if not matcher:
            return {"keyword_groups": {}, "stats": {}, "error": "Matcher not available"}
        
        return {
            "keyword_groups": {
                "measure": list(matcher.measure_keywords),
                "product": list(matcher.product_keywords),
                "place_company": list(matcher.place_company_keywords)
            },
            "stats": matcher.get_keyword_stats()
        }
    except Exception as e:
        logger.error(f"Error getting keywords: {e}")
        return {"error": str(e)}

@app.post("/api/scrape")
async def trigger_scrape(force_full_2024: bool = False, force_current_year: bool = False):
    """Trigger a scraping run."""
    try:
        if not scraper or not hasattr(scraper, 'scrape'):
            return {"status": "error", "message": "Scraper not available"}
        
        logger.info("Manual scrape triggered")
        logger.info(f"Scrape request - scraper data_dir: {scraper.data_dir}")
        logger.info(f"Scrape request - results_file: {scraper.results_file}")
        
        result = scraper.scrape(force_full_2024=force_full_2024, force_current_year=force_current_year)
        
        # Log post-scrape state
        logger.info(f"Scrape completed - results_file exists: {os.path.exists(scraper.results_file)}")
        if os.path.exists(scraper.results_file):
            import os
            logger.info(f"Scrape completed - file size: {os.path.getsize(scraper.results_file)} bytes")
        
        return result
    except Exception as e:
        logger.error(f"Error during manual scrape: {e}")
        return {"status": "error", "message": f"Error during scraping: {str(e)}"}

@app.get("/api/export/csv")
async def export_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Export filtered results as CSV."""
    try:
        if not scraper:
            return Response(content="Scraper not available", media_type="text/plain")
        
        filters = {}
        if start_date: filters['start_date'] = start_date
        if end_date: filters['end_date'] = end_date
        if author: filters['author'] = author
        if company: filters['company'] = company
        if product: filters['product'] = product
        if search: filters['search'] = search
        
        csv_content = scraper.export_csv(filters)
        
        if not csv_content:
            return Response(content="No data found", media_type="text/plain")
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=eurlex_trade_documents_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return Response(content=f"Error exporting data: {str(e)}", media_type="text/plain")

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Get a specific document."""
    try:
        if not scraper:
            raise HTTPException(status_code=503, detail="Scraper not available")
        
        results = scraper._load_results()
        document = next((doc for doc in results if doc.get('document_number') == document_id), None)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@app.get("/api/authors")
async def get_authors():
    """Get available authors."""
    try:
        if not scraper:
            return {"authors": []}
        
        results = scraper._load_results()
        authors = list(set(doc.get('author', 'unknown') for doc in results if doc.get('author')))
        return {"authors": authors}
    except Exception as e:
        logger.error(f"Error getting authors: {e}")
        return {"authors": [], "error": str(e)}

@app.get("/api/companies")
async def get_companies():
    """Get available companies."""
    try:
        if not scraper:
            return {"companies": []}
        
        results = scraper._load_results()
        companies = set()
        for doc in results:
            for company in doc.get('companies', []):
                if company:
                    companies.add(str(company))
        return {"companies": list(companies)}
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        return {"companies": [], "error": str(e)}

@app.get("/api/products")
async def get_products():
    """Get available products."""
    try:
        if not scraper:
            return {"products": []}
        
        results = scraper._load_results()
        products = set()
        for doc in results:
            for product in doc.get('products', []):
                if product:
                    products.add(str(product))
        return {"products": list(products)}
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return {"products": [], "error": str(e)}

@app.get("/api/connection-test")
async def test_connection():
    """Test EUR-Lex SOAP connection."""
    try:
        if not scraper or not hasattr(scraper, 'test_connection'):
            return {"status": "error", "message": "Scraper not available"}
        result = scraper.test_connection()
        return result
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return {"status": "error", "message": f"Connection test failed: {str(e)}"}

# Vercel will automatically detect this FastAPI app
