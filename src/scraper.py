"""
EUR-Lex Trade Document Scraper
Main orchestration logic for scraping and processing EUR-Lex documents.
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

try:
    from .matcher import EURLexTradeDocumentMatcher
    from .adapters.eurlex_web import EURLexWebClient
except ImportError:
    # Fallback for direct execution
    from matcher import EURLexTradeDocumentMatcher
    from adapters.eurlex_web import EURLexWebClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EURLexTradeScraper:
    """Main scraper class for EUR-Lex trade documents."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.matcher = EURLexTradeDocumentMatcher()
        self.web_client = EURLexWebClient()
        self.current_year = datetime.now().year
        
        # File paths
        self.results_file = self.data_dir / f"results-{self.current_year}.json"
        self.state_file = self.data_dir / "state.json"
        
        # Initialize data files if they don't exist
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Initialize data files if they don't exist."""
        # Initialize results file
        if not self.results_file.exists():
            self._save_results([])
            logger.info(f"Initialized results file: {self.results_file}")
        
        # Initialize state file
        if not self.state_file.exists():
            self._save_state({
                "last_checked_date": None,
                "last_run": None,
                "total_documents": 0
            })
            logger.info(f"Initialized state file: {self.state_file}")
    
    def _load_results(self) -> List[Dict]:
        """Load existing results from JSON file."""
        try:
            if self.results_file.exists():
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading results: {e}")
            return []
    
    def _save_results(self, results: List[Dict]):
        """Save results to JSON file."""
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Saved {len(results)} results to {self.results_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def _load_state(self) -> Dict:
        """Load application state from JSON file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return {}
    
    def _save_state(self, state: Dict):
        """Save application state to JSON file."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Saved state: {state}")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def _get_date_range(self) -> Tuple[date, date]:
        """Determine date range for scraping based on last run."""
        state = self._load_state()
        today = date.today()
        
        if state.get("last_checked_date"):
            try:
                last_date = datetime.strptime(state["last_checked_date"], "%Y-%m-%d").date()
                from_date = last_date + timedelta(days=1)
            except ValueError:
                logger.warning("Invalid last_checked_date in state, starting from 2024")
                from_date = date(2024, 1, 1)
        else:
            # First run - start from beginning of 2024
            from_date = date(2024, 1, 1)
        
        return from_date, today
    
    def _deduplicate_documents(self, existing: List[Dict], new: List[Dict]) -> List[Dict]:
        """Remove duplicates based on document number (DN) and other identifiers."""
        
        # Create sets of existing document identifiers
        existing_dns = {doc.get('DN') for doc in existing if doc.get('DN')}
        existing_titles = {doc.get('TI') for doc in existing if doc.get('TI')}
        
        # Track duplicate statistics
        duplicates_by_dn = 0
        duplicates_by_title = 0
        unique_new = []
        
        for doc in new:
            doc_number = doc.get('DN')
            title = doc.get('TI')
            
            # Check for duplicates by document number (primary check)
            if doc_number and doc_number in existing_dns:
                duplicates_by_dn += 1
                logger.debug(f"Duplicate by DN: {doc_number}")
                continue
                
            # Check for duplicates by title (secondary check for docs without DN)
            if not doc_number and title and title in existing_titles:
                duplicates_by_title += 1
                logger.debug(f"Duplicate by title: {title[:50]}...")
                continue
            
            # Document is unique
            unique_new.append(doc)
            
            # Add to existing sets for future checks in this batch
            if doc_number:
                existing_dns.add(doc_number)
            if title:
                existing_titles.add(title)
        
        # Log detailed deduplication results
        total_duplicates = duplicates_by_dn + duplicates_by_title
        logger.info(f"Deduplication: {len(new)} new -> {len(unique_new)} unique")
        if total_duplicates > 0:
            logger.info(f"Removed {total_duplicates} duplicates: {duplicates_by_dn} by DN, {duplicates_by_title} by title")
        
        return unique_new
    
    def _clean_existing_duplicates(self, documents: List[Dict]) -> List[Dict]:
        """Remove duplicates from existing document list."""
        if not documents:
            return documents
            
        seen_dns = set()
        seen_titles = set()
        cleaned = []
        duplicates_removed = 0
        
        for doc in documents:
            doc_number = doc.get('DN')
            title = doc.get('TI')
            
            # Check for duplicates by document number
            if doc_number:
                if doc_number in seen_dns:
                    duplicates_removed += 1
                    logger.debug(f"Removing duplicate DN: {doc_number}")
                    continue
                seen_dns.add(doc_number)
            
            # Check for duplicates by title (for docs without DN)
            elif title:
                if title in seen_titles:
                    duplicates_removed += 1
                    logger.debug(f"Removing duplicate title: {title[:50]}...")
                    continue
                seen_titles.add(title)
            
            cleaned.append(doc)
        
        if duplicates_removed > 0:
            logger.info(f"Cleaned {duplicates_removed} duplicates from existing {len(documents)} documents")
            
        return cleaned
    
    def _enrich_documents(self, documents: List[Dict]) -> List[Dict]:
        """Enrich documents with additional metadata."""
        enriched = []
        
        for doc in documents:
            # Add scraping timestamp
            doc['scraped_at'] = datetime.now().isoformat()
            
            # Extract entities using matcher
            entities = self.matcher.extract_entities(doc)
            doc['companies'] = entities['companies']
            doc['products'] = entities['products']
            
            # Normalize field names for consistency
            doc['document_number'] = doc.get('DN', '')
            doc['title'] = doc.get('TI', '')
            doc['publication_date'] = doc.get('DD', '')
            doc['author'] = doc.get('AU', '')
            doc['form'] = doc.get('FM', '')
            doc['subject'] = doc.get('SU', '')
            doc['text'] = doc.get('TX', '')
            doc['text_excerpt'] = doc.get('TE', '')
            doc['official_journal'] = doc.get('OJ', '')
            
            # Generate EUR-Lex URL
            if doc.get('DN'):
                doc['eurlex_url'] = f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{doc['DN']}"
            
            enriched.append(doc)
        
        return enriched
    
    def scrape(self, force_full_2024: bool = False, force_current_year: bool = False) -> Dict:
        """
        Main scraping method.
        
        Args:
            force_full_2024: If True, scrape from start of 2024 regardless of last run
            force_current_year: If True, scrape from start of current year only
        
        Returns:
            Dictionary with scraping results and statistics
        """
        start_time = datetime.now()
        logger.info("Starting EUR-Lex trade document scraping")
        
        try:
            # Determine date range
            if force_current_year:
                current_year = date.today().year
                from_date = date(current_year, 1, 1)
                to_date = date.today()
                logger.info(f"Force scraping current year: {current_year}")
            elif force_full_2024:
                from_date = date(2024, 1, 1)
                to_date = date.today()
                logger.info("Force scraping from 2024-01-01")
            else:
                from_date, to_date = self._get_date_range()
            
            # Check if we're already up to date
            if from_date > to_date:
                logger.info("No new dates to scrape - already up to date")
                existing_results = self._load_results()
                self._save_state({
                    "last_checked_date": to_date.isoformat(),
                    "last_run": datetime.now().isoformat(),
                    "total_documents": len(existing_results)
                })
                return {
                    "status": "up_to_date",
                    "message": "Already up to date! No new dates to scrape.",
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat(),
                    "last_checked_date": to_date.isoformat(),
                    "new_documents": 0,
                    "total_documents": len(existing_results),
                    "duration_seconds": 0
                }
            
            logger.info(f"Scraping EUR-Lex from {from_date} to {to_date}")
            
            # Fetch documents from EUR-Lex web search
            raw_documents = self.web_client.search_trade_regulations(
                date_from=from_date,
                date_to=to_date,
                max_pages=10  # Limit to 10 pages for safety
            )
            
            logger.info(f"Retrieved {len(raw_documents)} raw documents from EUR-Lex")
            
            # Apply keyword matching
            matched_documents = self.matcher.filter_documents(raw_documents)
            logger.info(f"Keyword matching: {len(raw_documents)} -> {len(matched_documents)} matches")
            
            # Enrich documents with metadata
            enriched_documents = self._enrich_documents(matched_documents)
            
            # Load existing results and clean any duplicates
            existing_results = self._load_results()
            existing_results = self._clean_existing_duplicates(existing_results)
            unique_new = self._deduplicate_documents(existing_results, enriched_documents)
            
            # Combine and save results
            if unique_new:
                all_results = existing_results + unique_new
                # Sort by publication date (newest first)
                all_results.sort(key=lambda x: x.get('publication_date', ''), reverse=True)
                self._save_results(all_results)
                logger.info(f"Added {len(unique_new)} new documents, total: {len(all_results)}")
            else:
                all_results = existing_results
                logger.info("No new documents to add")
            
            # Always update state with latest run info
            latest_date = to_date.strftime('%Y-%m-%d')
            self._save_state({
                "last_checked_date": latest_date,
                "last_run": datetime.now().isoformat(),
                "total_documents": len(all_results)
            })
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "message": f"Successfully scraped {len(unique_new)} new documents",
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat(),
                "last_checked_date": latest_date,
                "new_documents": len(unique_new),
                "total_documents": len(all_results),
                "raw_documents_fetched": len(raw_documents),
                "matched_documents": len(matched_documents),
                "duration_seconds": round(duration, 2)
            }
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return {
                "status": "error",
                "message": f"Scraping failed: {str(e)}",
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
    
    def get_statistics(self) -> Dict:
        """Get overall statistics about scraped data."""
        try:
            results = self._load_results()
            state = self._load_state()
            
            if not results:
                return {
                    "total_documents": 0,
                    "last_run": state.get("last_run"),
                    "last_checked_date": state.get("last_checked_date"),
                    "date_range": {"earliest": None, "latest": None},
                    "document_types": {},
                    "authors": {},
                    "companies": {},
                    "products": {}
                }
            
            # Calculate date range
            dates = [doc.get('publication_date') for doc in results if doc.get('publication_date')]
            dates = [d for d in dates if d]  # Remove empty dates
            
            # Count document types
            doc_types = {}
            for doc in results:
                doc_type = doc.get('form', 'Unknown')
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Count authors
            authors = {}
            for doc in results:
                author = doc.get('author', 'Unknown')
                authors[author] = authors.get(author, 0) + 1
            
            # Count companies and products
            companies = {}
            products = {}
            
            for doc in results:
                for company in doc.get('companies', []):
                    companies[company] = companies.get(company, 0) + 1
                
                for product in doc.get('products', []):
                    products[product] = products.get(product, 0) + 1
            
            return {
                "total_documents": len(results),
                "last_run": state.get("last_run"),
                "last_checked_date": state.get("last_checked_date"),
                "date_range": {
                    "earliest": min(dates) if dates else None,
                    "latest": max(dates) if dates else None
                },
                "document_types": dict(sorted(doc_types.items(), key=lambda x: x[1], reverse=True)),
                "authors": dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
                "companies": dict(sorted(companies.items(), key=lambda x: x[1], reverse=True)),
                "products": dict(sorted(products.items(), key=lambda x: x[1], reverse=True))
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}
    
    def _apply_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to results."""
        filtered = results
        
        # Date range filter
        if filters.get('start_date'):
            filtered = [doc for doc in filtered 
                       if doc.get('publication_date', '') >= filters['start_date']]
        
        if filters.get('end_date'):
            filtered = [doc for doc in filtered 
                       if doc.get('publication_date', '') <= filters['end_date']]
        
        # Author filter
        if filters.get('author'):
            filtered = [doc for doc in filtered 
                       if filters['author'].lower() in doc.get('author', '').lower()]
        
        # Company filter
        if filters.get('company'):
            filtered = [doc for doc in filtered 
                       if any(filters['company'].lower() in company.lower() 
                             for company in doc.get('companies', []))]
        
        # Product filter
        if filters.get('product'):
            filtered = [doc for doc in filtered 
                       if any(filters['product'].lower() in product.lower() 
                             for product in doc.get('products', []))]
        
        # Search filter (title and text)
        if filters.get('search'):
            search_term = filters['search'].lower()
            filtered = [doc for doc in filtered 
                       if search_term in doc.get('title', '').lower() 
                       or search_term in doc.get('text', '').lower()]
        
        return filtered
    
    def export_csv(self, filters: Dict = None) -> str:
        """Export filtered results as CSV."""
        try:
            results = self._load_results()
            
            if filters:
                results = self._apply_filters(results, filters)
            
            if not results:
                return ""
            
            # CSV header
            csv_lines = [
                "Publication Date,Title,Type,Document Number,Author,EUR-Lex URL,Companies,Products,Excerpts,Scraped At,Measure Keywords,Product Keywords,Place/Company Keywords,Groups Matched,Total Groups,Matched Text Snippets"
            ]
            
            for doc in results:
                def escape_csv_value(value):
                    if not value:
                        return ''
                    str_value = str(value)
                    if '"' in str_value or ',' in str_value or '\n' in str_value or '\r' in str_value:
                        escaped = str_value.replace('"', '""')
                        return f'"{escaped}"'
                    return str_value
                
                # Extract match details
                match_details = doc.get('match_details', {})
                
                # Clean and format text fields
                title = doc.get('title', '').replace('\n', ' ').replace('\r', ' ')
                text_excerpt = doc.get('text_excerpt', '').replace('\n', ' ').replace('\r', ' ')[:200]
                
                # Format keyword lists
                measure_keywords = '; '.join(match_details.get('measure_keywords', []))
                product_keywords = '; '.join(match_details.get('product_keywords', []))
                place_keywords = '; '.join(match_details.get('place_company_keywords', []))
                matched_snippets = '; '.join(match_details.get('matched_text_snippets', []))
                
                # Format company and product lists
                company_list = [str(company) for company in doc.get('companies', [])]
                product_list = [str(product) for product in doc.get('products', [])]
                
                row = [
                    doc.get('publication_date', ''),
                    escape_csv_value(title),
                    doc.get('form', ''),
                    doc.get('document_number', ''),
                    escape_csv_value(doc.get('author', '')),
                    doc.get('eurlex_url', ''),
                    '; '.join(company_list),
                    '; '.join(product_list),
                    escape_csv_value(text_excerpt),
                    doc.get('scraped_at', ''),
                    measure_keywords,
                    product_keywords,
                    place_keywords,
                    str(match_details.get('groups_matched', '')),
                    str(match_details.get('total_groups', '')),
                    escape_csv_value(matched_snippets)
                ]
                
                csv_lines.append(','.join(row))
            
            return '\n'.join(csv_lines)
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return f"Error exporting data: {str(e)}"
    
    def test_connection(self) -> Dict:
        """Test EUR-Lex SOAP connection."""
        return self.soap_client.test_connection()
