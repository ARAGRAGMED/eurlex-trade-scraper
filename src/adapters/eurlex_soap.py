"""
EUR-Lex SOAP Webservice Client
Handles communication with EUR-Lex SOAP API for document search and retrieval.
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
import xml.etree.ElementTree as ET
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EURLexSOAPClient:
    """SOAP client for EUR-Lex webservice."""
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        try:
            # Look for .env file in current directory or project root
            env_paths = [
                Path('.env'),
                Path(__file__).parent.parent.parent / '.env'  # Project root
            ]
            
            for env_path in env_paths:
                if env_path.exists():
                    logger.debug(f"Loading environment from {env_path}")
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                if key and not os.getenv(key):  # Don't override existing env vars
                                    os.environ[key] = value
                    break
        except Exception as e:
            logger.debug(f"Could not load .env file: {e}")
    
    def __init__(self, username: str = None, password: str = None, wsdl_url: str = None):
        """Initialize EUR-Lex SOAP client."""
        
        # Try to load from .env file first
        self._load_env_file()
        
        # Get credentials from environment or parameters
        self.username = username or os.getenv('EURLEX_USERNAME')
        self.password = password or os.getenv('EURLEX_PASSWORD')
        self.wsdl_url = wsdl_url or os.getenv('EURLEX_WSDL_URL', 'https://eur-lex.europa.eu/EURLexWebService?wsdl')
        
        if not all([self.username, self.password]):
            logger.warning("EUR-Lex credentials not provided. Some operations may fail.")
        
        # Try to import zeep for SOAP client
        self.client = None
        try:
            from zeep import Client, Settings
            from zeep.transports import Transport
            from requests import Session
            from requests.auth import HTTPBasicAuth
            
            # Set up SOAP client with authentication
            session = Session()
            if self.username and self.password:
                session.auth = HTTPBasicAuth(self.username, self.password)
            
            # Configure transport and settings
            transport = Transport(session=session)
            settings = Settings(strict=False, xml_huge_tree=True)
            
            self.client = Client(self.wsdl_url, transport=transport, settings=settings)
            logger.info(f"EUR-Lex SOAP client initialized successfully")
        except ImportError:
            logger.error("zeep library not available. Install with: pip install zeep")
        except Exception as e:
            logger.error(f"Failed to initialize EUR-Lex SOAP client: {e}")
    
    def build_trade_regulation_query(
        self,
        date_from: date = None,
        date_to: date = None,
        limit: int = 100
    ) -> str:
        """Build specific query for trade regulations (antidumping, CVD, etc.)."""
        
        # Define our keyword groups
        measure_keywords = [
            "antidumping", "countervailing duty", "CVD", "anti-subsidy", 
            "safeguard", "review", "sunset review", "circumvention", 
            "antitrust", "sanctions"
        ]
        
        product_keywords = [
            "phosphate", "phosphate rock", "phosphoric acid", "fertiliz*",
            "DAP", "MAP", "TSP", "SSP", "HS25*", "HS31*", "3103", "3105"
        ]
        
        entity_keywords = [
            "Morocco", "OCP", "Mosaic", "Nutrien", "Yara", "ICL", 
            "Maaden", "Eurochem", "Phosagro", "CFIndustries", "Jordan Phosphate"
        ]
        
        # Build keyword conditions
        measure_conditions = [f"(TI CONTAINS '{kw}' OR TX CONTAINS '{kw}')" for kw in measure_keywords]
        product_conditions = [f"(TI CONTAINS '{kw}' OR TX CONTAINS '{kw}')" for kw in product_keywords]
        entity_conditions = [f"(TI CONTAINS '{kw}' OR TX CONTAINS '{kw}')" for kw in entity_keywords]
        
        # Combine with AND logic (all three groups must match)
        where_conditions = [
            f"({' OR '.join(measure_conditions)})",
            f"({' OR '.join(product_conditions)})",
            f"({' OR '.join(entity_conditions)})"
        ]
        
        # Add date range
        if date_from:
            where_conditions.append(f"DD >= '{date_from.strftime('%Y-%m-%d')}'")
        if date_to:
            where_conditions.append(f"DD <= '{date_to.strftime('%Y-%m-%d')}'")
        
        # Focus on trade-relevant document types
        document_type_conditions = [
            "FM = 'REG'",      # Regulations (main trade measures)
            "FM = 'DEC'",      # Decisions (Commission trade decisions)
            "FM = 'DIR'",      # Directives (trade policy)
            "FM = 'COM'",      # Communications (preparatory docs)
            "FM = 'SWD'",      # Staff working documents
            "FM = 'JOIN'"      # Joint communications
        ]
        where_conditions.append(f"({' OR '.join(document_type_conditions)})")
        
        # Focus on DG Trade and related authorities
        author_conditions = [
            "AU CONTAINS 'Commission'",
            "AU CONTAINS 'DG Trade'", 
            "AU CONTAINS 'Directorate-General for Trade'",
            "AU CONTAINS 'European Commission'"
        ]
        where_conditions.append(f"({' OR '.join(author_conditions)})")
        
        where_clause = ' AND '.join(where_conditions)
        
        query = f"""
        SELECT DN, TI, DD, AU, OJ, FM, SU, TX, TE, RJ, LB, DF, DG, DT
        FROM EURLEX 
        WHERE {where_clause}
        ORDER BY DD DESC
        """
        
        return query.strip()
    
    def search_documents(
        self,
        query: str,
        language: str = "EN",
        page: int = 1,
        page_size: int = 100
    ) -> Dict:
        """Execute search query via SOAP webservice."""
        
        if not self.client:
            logger.warning("SOAP client not initialized - returning empty results")
            return {
                "documents": [],
                "total_count": 0,
                "page_info": {"current_page": 1, "page_size": 0},
                "error": "SOAP client not available"
            }
        
        try:
            logger.info(f"Executing EUR-Lex search query (page {page}, size {page_size})")
            logger.debug(f"Query: {query}")
            
            # Call the SOAP webservice using the correct method name and parameters
            response = self.client.service.doQuery(
                expertQuery=query,
                page=page,
                pageSize=page_size,
                searchLanguage=language,
                limitToLatestConsleg="false",
                excludeAllConsleg="false",
                showDocumentsAvailableIn=""
            )
            
            logger.info(f"Search completed successfully")
            return self._parse_search_response(response)
            
        except Exception as e:
            logger.error(f"Error executing search query: {e}")
            return {
                "documents": [],
                "total_count": 0,
                "page_info": {"current_page": 1, "page_size": 0},
                "error": str(e)
            }
    
    def _parse_search_response(self, response) -> Dict:
        """Parse SOAP response into structured data."""
        
        try:
            # Handle different response formats
            if hasattr(response, 'results'):
                results = response.results
            elif hasattr(response, 'return'):
                results = getattr(response, 'return')
            else:
                results = response
            
            documents = []
            
            # Parse XML results if needed
            if isinstance(results, str):
                root = ET.fromstring(results)
                # Extract document data from XML
                for doc_elem in root.findall('.//document'):
                    doc_data = {}
                    for child in doc_elem:
                        doc_data[child.tag] = child.text
                    documents.append(doc_data)
            elif isinstance(results, list):
                documents = results
            elif hasattr(results, '__iter__'):
                documents = list(results)
            
            return {
                "documents": documents,
                "total_count": len(documents),
                "page_info": {
                    "current_page": 1,
                    "page_size": len(documents)
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing search response: {e}")
            return {
                "documents": [],
                "total_count": 0,
                "page_info": {"current_page": 1, "page_size": 0},
                "error": str(e)
            }
    
    def search_trade_regulations(
        self,
        date_from: date = None,
        date_to: date = None,
        language: str = "EN"
    ) -> List[Dict]:
        """Search for trade regulations with our specific criteria."""
        
        # Default to last 3 months if no date range provided
        if not date_from:
            date_from = date.today() - timedelta(days=90)
        if not date_to:
            date_to = date.today()
        
        if not self.client:
            logger.warning("SOAP client not available - returning empty results")
            return []
        
        query = self.build_trade_regulation_query(date_from, date_to)
        
        all_documents = []
        page = 1
        page_size = 100
        
        while True:
            try:
                result = self.search_documents(query, language, page, page_size)
                documents = result.get("documents", [])
                
                if not documents:
                    break
                
                all_documents.extend(documents)
                
                # Check if we got a full page (more results might be available)
                if len(documents) < page_size:
                    break
                
                page += 1
                
                # Safety limit
                if page > 10:  # Max 1000 documents
                    logger.warning("Reached maximum page limit")
                    break
                    
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                break
        
        logger.info(f"Retrieved {len(all_documents)} documents from EUR-Lex")
        return all_documents
    
    def test_connection(self) -> Dict:
        """Test SOAP webservice connection."""
        
        try:
            if not self.client:
                return {"status": "error", "message": "SOAP client not initialized"}
            
            # Try a simple query
            test_query = "SELECT DN, TI FROM EURLEX WHERE DD >= '2024-01-01' ORDER BY DD DESC"
            result = self.search_documents(test_query, page_size=1)
            
            return {
                "status": "success",
                "message": "EUR-Lex SOAP connection successful",
                "test_results": len(result.get("documents", 0))
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"EUR-Lex SOAP connection failed: {str(e)}"
            }
