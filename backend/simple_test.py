#!/usr/bin/env python3
"""
Simple test script for CarPrompt API that doesn't require pytest.
This script tests the basic functionality by importing modules and checking structure.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from app.main import app
        from app.models import Base, CarListing, Garage, SearchLog
        from app.database import get_db
        from app.ai import parse_prompt, get_embedding
        from app.routes.search import SearchRequest, CarResult
        from app.routes.listings import ListingCreate
        from app.routes.garages import GarageCreate
        
        print("✅ All modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Note: You need to install dependencies first:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_schema():
    """Test that Pydantic schemas have correct fields."""
    print("\nTesting Pydantic schemas...")
    
    try:
        from app.routes.search import SearchRequest, CarResult
        from app.routes.listings import ListingCreate
        from app.routes.garages import GarageCreate
        
        # Check SearchRequest
        assert hasattr(SearchRequest, 'prompt'), "SearchRequest should have 'prompt' field"
        
        # Check CarResult has required fields
        car_result_fields = ['id', 'title', 'make', 'model', 'year', 'price']
        for field in car_result_fields:
            assert hasattr(CarResult, field), f"CarResult should have '{field}' field"
        
        # Check ListingCreate has required fields
        listing_fields = ['title', 'make', 'model', 'year', 'price']
        for field in listing_fields:
            assert hasattr(ListingCreate, field), f"ListingCreate should have '{field}' field"
        
        # Check GarageCreate has required fields
        garage_fields = ['name', 'email']
        for field in garage_fields:
            assert hasattr(GarageCreate, field), f"GarageCreate should have '{field}' field"
        
        print("✅ Pydantic schemas have correct fields")
        return True
    except AssertionError as e:
        print(f"❌ Schema validation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_endpoint_routes():
    """Test that FastAPI app has expected routes."""
    print("\nTesting FastAPI routes...")
    
    try:
        from app.main import app
        
        # Get all routes
        routes = []
        for route in app.routes:
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, 'methods') else []
            })
        
        # Check for expected routes
        expected_paths = [
            "/",
            "/api/search/",
            "/api/listings/",
            "/api/listings/{listing_id}",
            "/api/garages/",
        ]
        
        found_paths = [r["path"] for r in routes]
        missing = []
        for expected in expected_paths:
            if expected not in found_paths:
                missing.append(expected)
        
        if missing:
            print(f"❌ Missing routes: {missing}")
            print(f"Found routes: {found_paths}")
            return False
        else:
            print("✅ All expected routes are registered")
            return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("CarPrompt API - Simple Structure Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_schema,
        test_endpoint_routes,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        sys.exit(0)
    else:
        print(f"❌ {passed}/{total} tests passed")
        print("\nTo run full tests with pytest:")
        print("  1. Install test dependencies: pip install -r requirements-test.txt")
        print("  2. Run: pytest tests/ -v")
        sys.exit(1)

if __name__ == "__main__":
    main()