#!/usr/bin/env python3
"""
Test EUR-Lex expert query syntax
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_expert_query():
    """Test EUR-Lex expert query with proper syntax."""
    
    print("🔍 Testing EUR-Lex Expert Query Syntax")
    print("=" * 50)
    
    try:
        from adapters.eurlex_soap import EURLexSOAPClient
        
        client = EURLexSOAPClient()
        
        if not client.client:
            print("❌ SOAP client not available")
            return False
        
        if not client.username or not client.password:
            print("❌ Credentials not configured")
            return False
        
        # Test different query formats
        test_queries = [
            # Simple query
            "regulation",
            
            # Field-specific query
            "TI:regulation",
            
            # Date range query
            "DD:[2024-01-01 TO 2024-12-31]",
            
            # Combined query
            "TI:regulation AND DD:[2024-01-01 TO 2024-12-31]",
            
            # Our trade-specific query (simplified)
            "TI:antidumping AND TI:phosphate"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Test {i}: {query}")
            try:
                response = client.client.service.doQuery(
                    expertQuery=query,
                    page=1,
                    pageSize=5,
                    searchLanguage="EN",
                    limitToLatestConsleg="false",
                    excludeAllConsleg="false",
                    showDocumentsAvailableIn=""
                )
                
                print(f"✅ Query successful!")
                print(f"📊 Total hits: {getattr(response, 'totalhits', 'unknown')}")
                print(f"📄 Results: {len(getattr(response, 'result', []))}")
                
                # Show first result if available
                if hasattr(response, 'result') and response.result:
                    first_result = response.result[0]
                    print(f"📋 Sample result fields: {[attr for attr in dir(first_result) if not attr.startswith('_')]}")
                
                return True  # At least one query worked
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
                continue
        
        print("\n❌ All queries failed")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_parsing():
    """Test parsing a successful response."""
    
    print("\n📋 Testing Response Parsing")
    print("-" * 30)
    
    try:
        from adapters.eurlex_soap import EURLexSOAPClient
        
        client = EURLexSOAPClient()
        
        # Try the simplest possible query
        query = "regulation"
        
        print(f"🔎 Testing query: {query}")
        
        response = client.client.service.doQuery(
            expertQuery=query,
            page=1,
            pageSize=3,
            searchLanguage="EN",
            limitToLatestConsleg="false",
            excludeAllConsleg="false",
            showDocumentsAvailableIn=""
        )
        
        print(f"✅ Raw response type: {type(response)}")
        print(f"📊 Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        if hasattr(response, 'result') and response.result:
            print(f"📄 Found {len(response.result)} results")
            
            # Examine first result
            first_result = response.result[0]
            print(f"📋 Result type: {type(first_result)}")
            print(f"🔍 Result attributes: {[attr for attr in dir(first_result) if not attr.startswith('_')]}")
            
            # Try to extract common fields
            common_fields = ['DN', 'TI', 'DD', 'AU', 'OJ', 'FM']
            for field in common_fields:
                if hasattr(first_result, field):
                    value = getattr(first_result, field)
                    print(f"  {field}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run EUR-Lex query tests."""
    
    print("🇪🇺 EUR-Lex Query Test")
    print("=" * 50)
    
    # Test 1: Expert query syntax
    query_ok = test_expert_query()
    
    if query_ok:
        # Test 2: Response parsing
        parse_ok = test_response_parsing()
        
        if parse_ok:
            print("\n🎉 EUR-Lex queries working!")
            print("✅ Ready to implement full scraper")
        else:
            print("\n⚠️  Queries work but parsing needs adjustment")
    else:
        print("\n❌ EUR-Lex queries not working")
        print("💡 Check query syntax or credentials")
    
    return query_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
