#!/usr/bin/env python3
"""
Test imports to ensure all modules can be loaded before starting the server
"""
import sys
import traceback

def test_imports():
    """Test critical imports that the application needs"""
    try:
        print("Testing imports...")
        
        # Test main application imports
        from src.routes.main import app
        print("✓ Main app import successful")
        
        # Test route imports
        from src.routes.crypto_data import crypto_router
        print("✓ Crypto router import successful")
        
        from src.routes.static_data import static_router
        print("✓ Static router import successful")
        
        # Test service imports
        from src.services.api_call_manager import ApiCallManager
        print("✓ API call manager import successful")
        
        from src.services.external_api_caller import ExternalApiCaller
        print("✓ External API caller import successful")
        
        # Test config imports
        from src.config.config import Config
        print("✓ Config import successful")
        
        # Test model imports
        from src.routes.models.schemas import CompareRequest
        print("✓ Schema models import successful")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
