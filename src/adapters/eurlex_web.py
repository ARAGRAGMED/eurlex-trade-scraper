"""
EUR-Lex Web Search Client
Uses the Advanced Search Form instead of SOAP for document retrieval.
"""

import requests
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
from urllib.parse import urlencode, quote
import time
import json
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EURLexWebClient:
    """Web scraping client for EUR-Lex Advanced Search."""
    
    def __init__(self, delay_between_requests: float = 1.0):
        """Initialize EUR-Lex web client."""
        
        self.base_url = "https://eur-lex.europa.eu"
        self.search_form_url = f"{self.base_url}/advanced-search-form.html"
        self.search_results_url = f"{self.base_url}/search.html"
        self.delay = delay_between_requests
        
        # Set up session with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logger.info("EUR-Lex web client initialized successfully")
    
    def build_search_params(
        self,
        keywords: List[str] = None,
        date_from: date = None,
        date_to: date = None,
        document_types: List[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """Build search parameters for EUR-Lex search results URL."""
        
        params = {
            'lang': 'en',
            'type': 'advanced',
            'DTS_SUBDOM': 'ALL_ALL',
            'DTS_DOM': 'ALL',
            'SUBDOM_INIT': 'ALL_ALL'
        }
        
        # Text search query - use a timestamp-based qid like the working example
        if keywords:
            # Build search query 
            search_text = ' AND '.join(keywords)
            # Use timestamp as qid (EUR-Lex seems to use this for query identification)
            import time
            params['qid'] = str(int(time.time() * 1000))  # Millisecond timestamp
            # Add the actual search text if there's a parameter for it
            params['text'] = search_text
        else:
            # Use a simple timestamp for general search
            import time
            params['qid'] = str(int(time.time() * 1000))
        
        # Document collection filters
        if document_types:
            # Map document types to EUR-Lex collection codes
            collections = []
            if any(dt in ['REG', 'DEC', 'DIR'] for dt in document_types):
                collections.append('LEGISLATION')
            if any(dt in ['COM', 'SWD'] for dt in document_types):
                collections.append('PRE_ACTS')
            
            if collections:
                params['DTS_SUBDOM'] = ','.join(collections)
        
        # Pagination - EUR-Lex might use different parameter names
        if page > 1:
            params['page'] = str(page)
        
        return params
    
    def build_trade_regulation_search(
        self,
        date_from: date = None,
        date_to: date = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """Build search specifically for trade regulations using simplified approach."""
        
        # Use the working URL pattern from the Morocco example
        params = {
            'SUBDOM_INIT': 'ALL_ALL',
            'DTS_SUBDOM': 'ALL_ALL', 
            'textScope0': 'ti',  # Search in title and text
            'DTS_DOM': 'ALL',
            'lang': 'en',
            'type': 'advanced'
        }
        
        # Add year filter for recent documents (use proper URL encoding)
        if date_from and date_from.year >= 2024:
            params['whOJ'] = f'YEAR_OJ_OLD={date_from.year}'
            params['whOJAba'] = f'YEAR_OJ_ABA={date_from.year}'
        else:
            # Default to current year
            current_year = date.today().year
            params['whOJ'] = f'YEAR_OJ_OLD={current_year}'
            params['whOJAba'] = f'YEAR_OJ_ABA={current_year}'
        
        # Use timestamp-based qid
        import time
        params['qid'] = str(int(time.time() * 1000))
        
        # Search for key entities/countries one at a time (simpler queries)
        # Start with Morocco as it has proven results
        params['andText0'] = 'Morocco'
        
        # Add pagination
        if page > 1:
            params['page'] = str(page)
        
        return params
    
    def search_documents(
        self,
        search_params: Dict,
        max_pages: int = 10
    ) -> List[Dict]:
        """Execute search and parse results."""
        
        all_documents = []
        
        for page_num in range(1, max_pages + 1):
            try:
                logger.info(f"Searching EUR-Lex page {page_num}")
                
                # Update page number
                search_params['page'] = str(page_num)
                
                # Make GET request to search results URL
                response = self.session.get(self.search_results_url, params=search_params, timeout=30)
                response.raise_for_status()
                
                # Parse results
                documents = self._parse_search_results(response.text)
                
                if not documents:
                    logger.info(f"No more results on page {page_num}")
                    break
                
                all_documents.extend(documents)
                logger.info(f"Found {len(documents)} documents on page {page_num}")
                
                # Rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error searching page {page_num}: {e}")
                break
        
        logger.info(f"Total documents retrieved: {len(all_documents)}")
        return all_documents
    
    def _parse_search_results(self, html_content: str) -> List[Dict]:
        """Parse EUR-Lex search results page into structured data."""
        
        documents = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find search result items - EUR-Lex uses different structure
            # Look for the main content area and result items
            result_items = soup.find_all('div', class_='SearchResult') or \
                          soup.find_all('li', class_='SearchResult') or \
                          soup.find_all('div', {'id': lambda x: x and 'result' in x.lower()})
            
            # If no SearchResult class, look for document titles/links
            if not result_items:
                # Look for document titles (h2, h3 with links)
                title_elements = soup.find_all(['h2', 'h3'], string=lambda text: text and any(word in text.lower() for word in ['regulation', 'decision', 'directive', 'communication']))
                
                for title_elem in title_elements:
                    # Find the parent container
                    container = title_elem.find_parent('div') or title_elem.find_parent('li')
                    if container:
                        result_items.append(container)
            
            # If still no results, look for any links to documents
            if not result_items:
                # Look for CELEX document links
                celex_links = soup.find_all('a', href=lambda href: href and ('eli' in href or 'celex' in href.lower()))
                for link in celex_links[:20]:  # Limit to first 20
                    container = link.find_parent(['div', 'li', 'article'])
                    if container and container not in result_items:
                        result_items.append(container)
            
            logger.info(f"Found {len(result_items)} potential result items")
            
            for item in result_items:
                doc_data = {}
                
                # Extract title - look for links or headings
                title_elem = item.find('a', href=lambda href: href and ('eli' in href or 'celex' in href.lower())) or \
                           item.find(['h1', 'h2', 'h3', 'h4']) or \
                           item.find('a')
                
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    if title_text and len(title_text) > 10:  # Filter out short/empty titles
                        doc_data['TI'] = title_text
                        
                        # Extract document URL
                        if title_elem.name == 'a' and title_elem.get('href'):
                            href = title_elem['href']
                            if href.startswith('/'):
                                doc_data['url'] = self.base_url + href
                            elif href.startswith('http'):
                                doc_data['url'] = href
                
                # Extract CELEX number
                celex_text = item.get_text()
                import re
                celex_match = re.search(r'(3\d{4}[A-Z]\d{4})', celex_text)
                if celex_match:
                    doc_data['DN'] = celex_match.group(1)
                
                # Extract date - look for date patterns
                date_matches = re.findall(r'(\d{1,2}[./]\d{1,2}[./]\d{4})', celex_text)
                if date_matches:
                    try:
                        date_str = date_matches[0].replace('.', '/')
                        doc_data['DD'] = datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                    except:
                        doc_data['DD'] = date_matches[0]
                
                # Extract document type from title or content
                doc_type = None
                title_lower = doc_data.get('TI', '').lower()
                if 'regulation' in title_lower:
                    doc_type = 'Regulation'
                elif 'decision' in title_lower:
                    doc_type = 'Decision'
                elif 'directive' in title_lower:
                    doc_type = 'Directive'
                elif 'communication' in title_lower:
                    doc_type = 'Communication'
                
                if doc_type:
                    doc_data['FM'] = doc_type
                
                # Extract text excerpt
                text_content = item.get_text(strip=True)
                if len(text_content) > 100:
                    doc_data['TE'] = text_content[:500] + '...' if len(text_content) > 500 else text_content
                
                # Set default author
                doc_data['AU'] = 'European Union'
                
                # Add timestamp
                doc_data['scraped_at'] = datetime.now().isoformat()
                
                # Only add if we have essential data
                if doc_data.get('TI') and (doc_data.get('DN') or doc_data.get('url')):
                    documents.append(doc_data)
            
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        
        logger.info(f"Parsed {len(documents)} documents from search results")
        return documents
    
    def search_trade_regulations(
        self,
        date_from: date = None,
        date_to: date = None,
        max_pages: int = 5
    ) -> List[Dict]:
        """Search for trade regulations with our specific criteria."""
        
        # Default to last 3 months if no date range provided
        if not date_from:
            date_from = date.today() - timedelta(days=90)
        if not date_to:
            date_to = date.today()
        
        logger.info(f"Searching EUR-Lex for trade regulations from {date_from} to {date_to}")
        
        # Build search parameters
        search_params = self.build_trade_regulation_search(
            date_from=date_from,
            date_to=date_to,
            page_size=20  # More results per page
        )
        
        # Execute search
        documents = self.search_documents(search_params, max_pages=max_pages)
        
        logger.info(f"Retrieved {len(documents)} documents from EUR-Lex web search")
        return documents
    
    def test_connection(self) -> Dict:
        """Test EUR-Lex web access."""
        
        try:
            # Test simple search using GET to results URL with working pattern
            import time
            test_params = {
                'lang': 'en',
                'type': 'advanced',
                'qid': str(int(time.time() * 1000)),  # Timestamp-based qid
                'DTS_SUBDOM': 'ALL_ALL',
                'DTS_DOM': 'ALL',
                'SUBDOM_INIT': 'ALL_ALL'
            }
            
            response = self.session.get(self.search_results_url, params=test_params, timeout=10)
            response.raise_for_status()
            
            # Check if we got results
            if 'SearchResult' in response.text or 'results' in response.text.lower():
                return {
                    "status": "success",
                    "message": "EUR-Lex web search connection successful",
                    "response_length": len(response.text)
                }
            else:
                return {
                    "status": "warning",
                    "message": "EUR-Lex accessible but no search results found"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"EUR-Lex web search connection failed: {str(e)}"
            }
