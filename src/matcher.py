"""
EUR-Lex Trade Document Matcher
Implements keyword matching logic for trade-related documents.
Uses the same 3-group AND logic as the Federal Register scraper.
"""

import re
import logging
from typing import Dict, List, Tuple, Set

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EURLexTradeDocumentMatcher:
    """Matches EUR-Lex documents against trade-related keywords."""
    
    def __init__(self):
        """Initialize keyword groups for trade document matching."""
        
        # Group A: Trade Measures
        self.measure_keywords = {
            "antidumping", "anti-dumping", "countervailing duty", "CVD", 
            "anti-subsidy", "safeguard", "regulation", "decision", "review", 
            "sunset review", "circumvention", "antitrust", "sanctions",
            "trade defence", "trade defense", "dumping", "subsidy"
        }
        
        # Group B: Products (phosphate and fertilizers)
        self.product_keywords = {
            "phosphate", "phosphate rock", "phosphoric acid", "fertilizer", 
            "fertiliser", "DAP", "MAP", "TSP", "SSP", "diammonium phosphate",
            "monoammonium phosphate", "triple superphosphate", "single superphosphate",
            "HS25", "HS31", "3103", "3105", "mineral fertilizer", "chemical fertilizer"
        }
        
        # Group C: Places and Companies
        self.place_company_keywords = {
            "Morocco", "OCP", "Mosaic", "Nutrien", "Yara", "ICL", "Maaden", 
            "Eurochem", "Phosagro", "CF Industries", "CFIndustries", 
            "Jordan Phosphate", "JPMC", "Moroccan", "Israel Chemicals",
            "PhosAgro", "EuroChem", "Nutrien Ltd", "The Mosaic Company"
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        if not text:
            return ""
        return text.lower().strip()
    
    def _find_keyword_matches(self, text: str, keywords: Set[str]) -> List[str]:
        """Find matching keywords in text."""
        if not text:
            return []
        
        normalized_text = self._normalize_text(text)
        matches = []
        
        for keyword in keywords:
            normalized_keyword = self._normalize_text(keyword)
            
            # Handle wildcard matching (e.g., fertiliz* matches fertilizer, fertiliser)
            if '*' in normalized_keyword:
                pattern = normalized_keyword.replace('*', r'\w*')
                if re.search(r'\b' + pattern + r'\b', normalized_text):
                    matches.append(keyword)
            else:
                # Word boundary matching for exact matches (prevents partial matches)
                # Also handle common prefixes like "inMorocco", "fromMorocco", etc.
                pattern = r'(?:\b|(?<=\bin)|(?<=\bfrom)|(?<=\bto)|(?<=\bof))' + re.escape(normalized_keyword) + r'\b'
                if re.search(pattern, normalized_text):
                    matches.append(keyword)
        
        return matches
    
    def _extract_matching_snippets(self, text: str, matched_keywords: List[str]) -> List[str]:
        """Extract text snippets around matched keywords."""
        if not text or not matched_keywords:
            return []
        
        snippets = []
        normalized_text = self._normalize_text(text)
        
        for keyword in matched_keywords:
            normalized_keyword = self._normalize_text(keyword)
            
            # Find keyword position
            if '*' in normalized_keyword:
                pattern = normalized_keyword.replace('*', r'\w*')
                match = re.search(r'\b' + pattern + r'\b', normalized_text)
            else:
                match = re.search(re.escape(normalized_keyword), normalized_text)
            
            if match:
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                snippet = text[start:end].strip()
                if snippet:
                    snippets.append(f"...{snippet}...")
        
        return snippets
    
    def is_match(self, document: Dict) -> Tuple[bool, Dict]:
        """
        Check if document matches our trade criteria.
        
        Implements modified logic: 
        - Group C (Places/Companies) is MANDATORY
        - Groups A (Measures) and B (Products) are OPTIONAL (at least one required)
        
        Args:
            document: EUR-Lex document with fields like TI (title), TX (text), etc.
        
        Returns:
            Tuple of (is_match, match_details)
        """
        
        # Combine searchable text fields
        searchable_text = " ".join([
            document.get('TI', ''),  # Title
            document.get('TX', ''),  # Text content
            document.get('SU', ''),  # Subject
            document.get('AU', ''),  # Author
            document.get('TE', ''),  # Text excerpt
        ])
        
        # Find matches in each keyword group
        measure_matches = self._find_keyword_matches(searchable_text, self.measure_keywords)
        product_matches = self._find_keyword_matches(searchable_text, self.product_keywords)
        place_company_matches = self._find_keyword_matches(searchable_text, self.place_company_keywords)
        
        # Modified logic: Group C (Places/Companies) is MANDATORY, Groups A & B are OPTIONAL
        # At least Group C + one other group must match
        is_match = (
            len(place_company_matches) > 0 and    # Group C: Places/Companies (MANDATORY)
            (len(measure_matches) > 0 or          # Group A: Measures (OPTIONAL)
             len(product_matches) > 0)            # Group B: Products (OPTIONAL)
        )
        
        # Calculate how many groups have matches (for display purposes)
        groups_with_matches = sum([
            len(measure_matches) > 0,
            len(product_matches) > 0,
            len(place_company_matches) > 0
        ])
        
        # Extract text snippets for matched keywords
        all_matched_keywords = measure_matches + product_matches + place_company_matches
        matched_text_snippets = self._extract_matching_snippets(searchable_text, all_matched_keywords)
        
        match_details = {
            "measure_keywords": measure_matches,
            "product_keywords": product_matches,
            "place_company_keywords": place_company_matches,
            "groups_matched": groups_with_matches,
            "total_groups": 3,
            "matched_text_snippets": matched_text_snippets[:3],  # Limit to 3 snippets
            "match_score": len(all_matched_keywords)  # Simple scoring
        }
        
        if is_match:
            logger.debug(f"Document matched: {document.get('DN', 'Unknown')} - "
                        f"Groups: {groups_with_matches}/3, Keywords: {len(all_matched_keywords)}")
        
        return is_match, match_details
    
    def filter_documents(self, documents: List[Dict]) -> List[Dict]:
        """Filter a list of documents, keeping only those that match our criteria."""
        
        matched_documents = []
        
        for doc in documents:
            is_match, match_details = self.is_match(doc)
            
            if is_match:
                # Add match details to the document
                doc['match_details'] = match_details
                doc['scraped_at'] = doc.get('scraped_at', None)  # Preserve if exists
                matched_documents.append(doc)
        
        logger.info(f"Filtered {len(documents)} documents -> {len(matched_documents)} matches")
        return matched_documents
    
    def get_keyword_stats(self) -> Dict:
        """Get statistics about keyword groups."""
        
        return {
            "measure_keywords_count": len(self.measure_keywords),
            "product_keywords_count": len(self.product_keywords),
            "place_company_keywords_count": len(self.place_company_keywords),
            "total_keywords": len(self.measure_keywords) + len(self.product_keywords) + len(self.place_company_keywords),
            "groups": {
                "measures": list(sorted(self.measure_keywords)),
                "products": list(sorted(self.product_keywords)),
                "places_companies": list(sorted(self.place_company_keywords))
            }
        }
    
    def extract_entities(self, document: Dict) -> Dict:
        """Extract companies and products mentioned in the document."""
        
        text = " ".join([
            document.get('TI', ''),
            document.get('TX', ''),
            document.get('SU', ''),
        ])
        
        # Find companies
        companies = []
        for keyword in self.place_company_keywords:
            if keyword in ["Morocco", "Moroccan"]:  # Skip country names for companies
                continue
            if self._normalize_text(keyword) in self._normalize_text(text):
                companies.append(keyword)
        
        # Find products
        products = []
        for keyword in self.product_keywords:
            if self._normalize_text(keyword) in self._normalize_text(text):
                products.append(keyword)
        
        return {
            "companies": list(set(companies)),
            "products": list(set(products))
        }
