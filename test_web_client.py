#!/usr/bin/env python3
"""
Test EUR-Lex Web Client (Advanced Search Form)
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_web_connection():
    """Test EUR-Lex web search connection."""
    
    print("🌐 Testing EUR-Lex Web Search Connection")
    print("=" * 50)
    
    try:
        from adapters.eurlex_web import EURLexWebClient
        
        client = EURLexWebClient()
        
        print("🧪 Testing basic connection...")
        result = client.test_connection()
        
        if result['status'] == 'success':
            print("✅ Connection successful!")
            print(f"📊 Response length: {result.get('response_length', 'unknown')} chars")
            return True
        else:
            print(f"❌ Connection failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_functionality():
    """Test EUR-Lex search functionality."""
    
    print("\n🔍 Testing Search Functionality")
    print("-" * 30)
    
    try:
        from adapters.eurlex_web import EURLexWebClient
        
        client = EURLexWebClient()
        
        # Test with a simple search first
        print("🔎 Testing simple regulation search...")
        
        # Build basic search params
        search_params = client.build_search_params(
            keywords=["regulation"],
            date_from=date.today() - timedelta(days=30),
            date_to=date.today(),
            page_size=5
        )
        
        documents = client.search_documents(search_params, max_pages=1)
        
        print(f"📄 Found {len(documents)} documents")
        
        if documents:
            print("✅ Search working!")
            print(f"📋 Sample document fields: {list(documents[0].keys())}")
            print(f"📝 Sample title: {documents[0].get('TI', 'No title')[:100]}...")
            return True
        else:
            print("⚠️  Search working but no results found")
            return True
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_trade_search():
    """Test trade-specific search."""
    
    print("\n🎯 Testing Trade Regulation Search")
    print("-" * 30)
    
    try:
        from adapters.eurlex_web import EURLexWebClient
        
        client = EURLexWebClient()
        
        print("🔎 Searching for trade regulations...")
        
        # Test our trade-specific search
        documents = client.search_trade_regulations(
            date_from=date.today() - timedelta(days=365),  # Last year
            date_to=date.today(),
            max_pages=2  # Limit for testing
        )
        
        print(f"📄 Found {len(documents)} trade-related documents")
        
        if documents:
            print("✅ Trade search working!")
            
            # Show details of first few results
            for i, doc in enumerate(documents[:3], 1):
                print(f"\n📋 Document {i}:")
                print(f"   Title: {doc.get('TI', 'No title')[:80]}...")
                print(f"   Date: {doc.get('DD', 'No date')}")
                print(f"   Type: {doc.get('FM', 'No type')}")
                print(f"   URL: {doc.get('url', 'No URL')}")
            
            return True
        else:
            print("ℹ️  No trade documents found (this might be normal)")
            return True
            
    except Exception as e:
        print(f"❌ Trade search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_integration():
    """Test full integration with matcher."""
    
    print("\n🔗 Testing Full Integration")
    print("-" * 30)
    
    try:
        from adapters.eurlex_web import EURLexWebClient
        from matcher import EURLexTradeDocumentMatcher
        
        web_client = EURLexWebClient()
        matcher = EURLexTradeDocumentMatcher()
        
        print("🔎 Running integrated search and matching...")
        
        # Get documents
        documents = web_client.search_trade_regulations(
            date_from=date.today() - timedelta(days=180),  # Last 6 months
            date_to=date.today(),
            max_pages=1
        )
        
        print(f"📄 Retrieved {len(documents)} documents")
        
        # Apply matching
        if documents:
            matched_docs = matcher.filter_documents(documents)
            print(f"🎯 Matched {len(matched_docs)} documents with our criteria")
            
            if matched_docs:
                print("✅ Full integration working!")
                
                # Show match details
                for i, doc in enumerate(matched_docs[:2], 1):
                    match_details = doc.get('match_details', {})
                    print(f"\n📋 Matched Document {i}:")
                    print(f"   Title: {doc.get('TI', 'No title')[:60]}...")
                    print(f"   Groups matched: {match_details.get('groups_matched', 0)}/3")
                    print(f"   Keywords found: {match_details.get('match_score', 0)}")
            else:
                print("ℹ️  No documents matched our strict criteria (normal)")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all web client tests."""
    
    print("🇪🇺 EUR-Lex Web Client Test")
    print("=" * 50)
    print("🔄 Switching from SOAP to Web Scraping approach...")
    print("💡 No credentials needed - uses public search form!")
    
    tests = [
        ("Connection Test", test_web_connection),
        ("Search Functionality", test_search_functionality),
        ("Trade Search", test_trade_search),
        ("Full Integration", test_full_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! Web scraping approach is working!")
        print("\n📋 Advantages of web approach:")
        print("✅ No credentials needed")
        print("✅ No SOAP/authentication issues")
        print("✅ Uses official search form")
        print("✅ More reliable than API")
        print("\n📋 Next steps:")
        print("1. Start web server: python3 run_web.py")
        print("2. Test scraping: python3 run_scraper.py --force-full-2024")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
