"""
Main FastAPI application for the EUR-Lex Trade Scraper.
Provides API endpoints and serves the dashboard.
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List
import logging
from pathlib import Path
import os
from datetime import datetime

try:
    from .scraper import EURLexTradeScraper
    from .matcher import EURLexTradeDocumentMatcher
    from .adapters.eurlex_web import EURLexWebClient
except ImportError:
    # Fallback for direct execution
    from scraper import EURLexTradeScraper
    from matcher import EURLexTradeDocumentMatcher
    from adapters.eurlex_web import EURLexWebClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Initialize scraper
scraper = EURLexTradeScraper()
matcher = EURLexTradeDocumentMatcher()

# Mount static files
web_dir = Path(__file__).parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main dashboard HTML."""
    html_file = web_dir / "index.html"
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>EUR-Lex Trade Scraper</title></head>
            <body>
                <h1>EUR-Lex Trade Scraper Dashboard</h1>
                <p>Dashboard files not found. Please check the web directory.</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "EUR-Lex Trade Scraper", 
        "platform": "FastAPI",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/dashboard-data")
async def get_dashboard_data(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    author: Optional[str] = Query(None, description="Author filter"),
    company: Optional[str] = Query(None, description="Company filter"),
    product: Optional[str] = Query(None, description="Product filter"),
    search: Optional[str] = Query(None, description="Search term"),
    limit: Optional[int] = Query(100, description="Maximum number of results")
):
    """Get filtered dashboard data."""
    try:
        # Build filters
        filters = {}
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if author:
            filters['author'] = author
        if company:
            filters['company'] = company
        if product:
            filters['product'] = product
        if search:
            filters['search'] = search
        
        # Get results with filters
        results = scraper._load_results()
        if filters:
            results = scraper._apply_filters(results, filters)
        
        # Apply limit
        if limit and limit > 0:
            results = results[:limit]
        
        # Get statistics
        stats = scraper.get_statistics()
        
        return {
            "results": results,
            "statistics": stats,
            "filters_applied": filters,
            "total_returned": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")


@app.get("/api/statistics")
async def get_statistics():
    """Get overall statistics about the scraped data."""
    try:
        return scraper.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")


@app.get("/api/keywords")
async def get_keywords():
    """Get information about the keyword groups used for matching."""
    try:
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
        raise HTTPException(status_code=500, detail=f"Error retrieving keywords: {str(e)}")


@app.post("/api/scrape")
async def trigger_scrape(force_full_2024: bool = False, force_current_year: bool = False):
    """Trigger a scraping run."""
    try:
        logger.info("Manual scrape triggered")
        result = scraper.scrape(force_full_2024=force_full_2024, force_current_year=force_current_year)
        return result
    except Exception as e:
        logger.error(f"Error during manual scrape: {e}")
        raise HTTPException(status_code=500, detail=f"Error during scraping: {str(e)}")


@app.get("/api/export/csv")
async def export_csv(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    author: Optional[str] = Query(None, description="Author filter"),
    company: Optional[str] = Query(None, description="Company filter"),
    product: Optional[str] = Query(None, description="Product filter"),
    search: Optional[str] = Query(None, description="Search term")
):
    """Export filtered results as CSV."""
    try:
        # Build filters
        filters = {}
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if author:
            filters['author'] = author
        if company:
            filters['company'] = company
        if product:
            filters['product'] = product
        if search:
            filters['search'] = search
        
        # Generate CSV
        csv_content = scraper.export_csv(filters)
        
        if not csv_content:
            return Response(content="No data found", media_type="text/plain")
        
        # Return CSV file
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=eurlex_trade_documents_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Get a specific document by document number."""
    try:
        results = scraper._load_results()
        # Look for document by document_number field
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
    """Get available document authors."""
    try:
        results = scraper._load_results()
        authors = list(set(doc.get('author', 'unknown') for doc in results if doc.get('author')))
        return {"authors": authors}
    except Exception as e:
        logger.error(f"Error getting authors: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving authors: {str(e)}")


@app.get("/api/companies")
async def get_companies():
    """Get available companies."""
    try:
        results = scraper._load_results()
        companies = set()
        for doc in results:
            for company in doc.get('companies', []):
                if company:
                    companies.add(str(company))
        return {"companies": list(companies)}
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving companies: {str(e)}")


@app.get("/api/products")
async def get_products():
    """Get available products."""
    try:
        results = scraper._load_results()
        products = set()
        for doc in results:
            for product in doc.get('products', []):
                if product:
                    products.add(str(product))
        return {"products": list(products)}
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")


@app.get("/api/connection-test")
async def test_connection():
    """Test EUR-Lex SOAP connection."""
    try:
        result = scraper.test_connection()
        return result
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return {"status": "error", "message": f"Connection test failed: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
