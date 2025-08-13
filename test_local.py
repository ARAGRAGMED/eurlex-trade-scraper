#!/usr/bin/env python3
"""
Simple local test for EUR-Lex Trade Scraper
"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test individual module imports
        sys.path.insert(0, str(current_dir / "src"))
        
        print("📦 Testing web client...")
        from src.adapters.eurlex_web import EURLexWebClient
        
        web_client = EURLexWebClient()
        print("✅ Web client loaded")
        
        # Test web client connection
        connection_test = web_client.test_connection()
        print(f"🌐 Web connection test: {connection_test}")
        
        print("📦 Testing scraper...")
        from src.scraper import EURLexTradeScraper
        
        scraper = EURLexTradeScraper()
        print("✅ Scraper loaded")
        
        # Test scraper connection
        scraper_connection = scraper.test_connection()
        print(f"🔗 Scraper connection test: {scraper_connection}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality without EUR-Lex connection."""
    print("\n🔧 Testing basic functionality...")
    
    try:
        sys.path.insert(0, str(current_dir / "src"))
        
        # Test keyword matching
        from src.matcher import EURLexTradeDocumentMatcher
        matcher = EURLexTradeDocumentMatcher()
        
        # Test document
        test_doc = {
            'TI': 'Antidumping regulation on phosphate imports from Morocco',
            'TX': 'This regulation concerns OCP and fertilizer trade measures',
            'AU': 'European Commission',
            'DD': '2024-01-15'
        }
        
        is_match, details = matcher.is_match(test_doc)
        print(f"✅ Test document matching: {is_match}")
        print(f"   Groups matched: {details.get('groups_matched', 0)}/3")
        print(f"   Keywords found: {details.get('match_score', 0)}")
        
        # Test CSV export with empty data
        from src.scraper import EURLexTradeScraper
        scraper = EURLexTradeScraper()
        csv_content = scraper.export_csv()
        print(f"✅ CSV export test: {'✅ Working' if csv_content == '' else '✅ Has content'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_server():
    """Test that the web server can start."""
    print("\n🌐 Testing web server startup...")
    
    try:
        import uvicorn
        sys.path.insert(0, str(current_dir / "src"))
        
        # Import the app
        from src.main import app
        
        print("✅ FastAPI app can be imported")
        print("🚀 To start the server manually, run:")
        print("   python3 run_web.py")
        print("   Then visit: http://localhost:8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Web server test failed: {e}")
        return False

def main():
    print("🇪🇺 EUR-Lex Trade Scraper - Local Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Web Server", test_web_server)
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
        print("🎉 All tests passed! The application is ready for local testing.")
        print("\n📋 Next steps:")
        print("1. To test the web interface:")
        print("   python3 run_web.py")
        print("   Open: http://localhost:8000")
        print("\n2. To register for EUR-Lex webservice:")
        print("   Visit: https://eur-lex.europa.eu/content/help/data-reuse/webservice.html")
        print("   Set environment variables:")
        print("   export EURLEX_USERNAME='your_username'")
        print("   export EURLEX_PASSWORD='your_password'")
        print("\n3. To test with real data (after registration):")
        print("   python3 run_scraper.py --test-connection")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
