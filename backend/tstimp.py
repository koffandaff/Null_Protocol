# test_imports.py
try:
    from config.settings import settings
    print("✅ config.settings import successful")
    print(f"App Name: {settings.APP_NAME}")
    
    from utils.security_tools import SecurityTools
    print("✅ utils.security_tools import successful")
    
    from service.Security_Service import SecurityService
    print("✅ services.Security_Service import successful")
    
    from routers.Security_Router import router
    print("✅ routers.Security_Router import successful")
    
    print("\n🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()