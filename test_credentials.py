#!/usr/bin/env python3
"""
Test EUR-Lex credentials and connection
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_credentials():
    """Test EUR-Lex credentials and connection."""
    
    print("🔑 Testing EUR-Lex Credentials")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Found .env file")
        
        # Load and display (masked) credentials
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if 'USERNAME' in key:
                        print(f"📧 Username: {value[:3]}***{value[-3:] if len(value) > 6 else '***'}")
                    elif 'PASSWORD' in key:
                        print(f"🔒 Password: {'*' * len(value)} ({len(value)} chars)")
    else:
        print("❌ No .env file found")
        print("💡 Create one with: cp env.example .env")
    
    print("\n🌐 Testing SOAP Connection")
    print("-" * 30)
    
    try:
        from adapters.eurlex_soap import EURLexSOAPClient
        
        # Initialize client
        client = EURLexSOAPClient()
        
        print(f"📡 Username configured: {'✅ Yes' if client.username else '❌ No'}")
        print(f"🔐 Password configured: {'✅ Yes' if client.password else '❌ No'}")
        print(f"🌍 WSDL URL: {client.wsdl_url}")
        
        if not client.username or not client.password:
            print("\n❌ Credentials missing!")
            print("💡 Set them in .env file:")
            print("   EURLEX_USERNAME=your_username")
            print("   EURLEX_PASSWORD=your_password")
            return False
        
        print("\n🧪 Testing connection...")
        result = client.test_connection()
        
        if result['status'] == 'success':
            print("✅ Connection successful!")
            print(f"📊 Test results: {result.get('test_results', 'N/A')}")
            return True
        else:
            print(f"❌ Connection failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_query():
    """Test a simple search query."""
    
    print("\n🔍 Testing Search Query")
    print("-" * 30)
    
    try:
        from adapters.eurlex_soap import EURLexSOAPClient
        from datetime import date, timedelta
        
        client = EURLexSOAPClient()
        
        if not client.username or not client.password:
            print("❌ Skipping search test - no credentials")
            return False
        
        # Test with a simple query
        print("🔎 Executing test search...")
        
        date_from = date.today() - timedelta(days=30)  # Last 30 days
        date_to = date.today()
        
        documents = client.search_trade_regulations(
            date_from=date_from,
            date_to=date_to
        )
        
        print(f"📄 Found {len(documents)} documents in last 30 days")
        
        if len(documents) > 0:
            print("✅ Search working!")
            print(f"📋 Sample document fields: {list(documents[0].keys()) if documents else 'None'}")
        else:
            print("ℹ️  No matching documents found (this is normal)")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all credential tests."""
    
    print("🇪🇺 EUR-Lex Credential Test")
    print("=" * 50)
    
    # Test 1: Check credentials
    creds_ok = test_credentials()
    
    if creds_ok:
        # Test 2: Test search
        search_ok = test_search_query()
        
        if search_ok:
            print("\n🎉 All tests passed!")
            print("✅ Your EUR-Lex setup is working correctly")
            print("\n📋 Next steps:")
            print("1. Start web server: python3 run_web.py")
            print("2. Run full scrape: python3 run_scraper.py --force-full-2024")
        else:
            print("\n⚠️  Connection works but search failed")
            print("💡 Check the SOAP query format or try again later")
    else:
        print("\n❌ Credential test failed")
        print("💡 Please check your .env file and EUR-Lex registration")
    
    return creds_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
