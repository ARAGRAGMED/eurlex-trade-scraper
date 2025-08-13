#!/usr/bin/env python3
"""
Command-line interface for EUR-Lex Trade Scraper.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Change to src directory for imports
os.chdir(project_root / "src")
from scraper import EURLexTradeScraper


def main():
    parser = argparse.ArgumentParser(description="EUR-Lex Trade Document Scraper")
    parser.add_argument(
        "--force-full-2024",
        action="store_true",
        help="Force scraping from 2024-01-01 regardless of last run"
    )
    parser.add_argument(
        "--force-current-year",
        action="store_true",
        help="Force scraping from start of current year only"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test EUR-Lex web connection"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about scraped data"
    )
    parser.add_argument(
        "--export-csv",
        metavar="FILENAME",
        help="Export all data to CSV file"
    )
    parser.add_argument(
        "--clean-duplicates",
        action="store_true",
        help="Clean duplicate documents from existing data"
    )
    
    args = parser.parse_args()
    
    print("🇪🇺 EUR-Lex Trade Scraper CLI")
    print("=" * 40)
    
    scraper = EURLexTradeScraper()
    
    if args.test_connection:
        print("🔍 Testing EUR-Lex web connection...")
        result = scraper.test_connection()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        return
    
    if args.stats:
        print("📊 Getting statistics...")
        stats = scraper.get_statistics()
        print(f"Total documents: {stats.get('total_documents', 0)}")
        print(f"Last run: {stats.get('last_run', 'Never')}")
        print(f"Date range: {stats.get('date_range', {}).get('earliest', 'N/A')} to {stats.get('date_range', {}).get('latest', 'N/A')}")
        
        doc_types = stats.get('document_types', {})
        if doc_types:
            print("\nDocument types:")
            for doc_type, count in list(doc_types.items())[:5]:
                print(f"  {doc_type}: {count}")
        
        return
    
    if args.export_csv:
        print(f"📥 Exporting to {args.export_csv}...")
        csv_content = scraper.export_csv()
        if csv_content:
            with open(args.export_csv, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            print(f"✅ Exported to {args.export_csv}")
        else:
            print("❌ No data to export")
        return
    
    if args.clean_duplicates:
        print("🧹 Cleaning duplicate documents...")
        existing_results = scraper._load_results()
        
        if not existing_results:
            print("📝 No existing documents to clean")
            return
            
        print(f"📊 Before cleaning: {len(existing_results)} documents")
        
        # Check for duplicates
        dns = [doc.get('DN') for doc in existing_results if doc.get('DN')]
        unique_dns = set(dns)
        dn_duplicates = len(dns) - len(unique_dns)
        
        titles = [doc.get('TI') for doc in existing_results if doc.get('TI')]
        unique_titles = set(titles)
        title_duplicates = len(titles) - len(unique_titles)
        
        total_duplicates = dn_duplicates + title_duplicates
        
        if total_duplicates == 0:
            print("✅ No duplicates found!")
            return
            
        print(f"🔍 Found {total_duplicates} duplicates:")
        print(f"   - {dn_duplicates} by document number")
        print(f"   - {title_duplicates} by title")
        
        # Clean duplicates
        cleaned_results = scraper._clean_existing_duplicates(existing_results)
        scraper._save_results(cleaned_results)
        
        print(f"📊 After cleaning: {len(cleaned_results)} documents")
        print(f"✅ Removed {len(existing_results) - len(cleaned_results)} duplicates")
        return
    
    # Default action: scrape
    print("🔄 Starting scraping...")
    result = scraper.scrape(
        force_full_2024=args.force_full_2024,
        force_current_year=args.force_current_year
    )
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"New documents: {result.get('new_documents', 0)}")
    print(f"Total documents: {result.get('total_documents', 0)}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")
    
    if result['status'] == 'error':
        sys.exit(1)


if __name__ == "__main__":
    main()
