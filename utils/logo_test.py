"""
Utility script to test if the logo can be loaded properly.
"""
import os
import base64
import sys

def find_logo():
    """
    Try to find the logo.png file in various locations.
    
    Returns:
        tuple: (found, path) - boolean indicating if found and path if found
    """
    # Possible locations to check
    locations = [
        os.path.join(os.getcwd(), "logo.png"),
        os.path.join(os.getcwd(), "static", "logo.png"),
        os.path.join(os.getcwd(), "assets", "logo.png"),
        os.path.join(os.path.dirname(os.getcwd()), "logo.png")
    ]
    
    # Check each location
    for path in locations:
        if os.path.exists(path):
            return True, path
    
    return False, None

def test_logo_loading():
    """
    Test if the logo can be loaded and encoded properly.
    """
    print("Testing logo loading...")
    found, path = find_logo()
    
    if found:
        print(f"✅ Logo found at: {path}")
        try:
            # Try to open and encode the logo
            with open(path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode()
                size = len(encoded)
                print(f"✅ Successfully encoded logo (size: {size} bytes)")
                return True
        except Exception as e:
            print(f"❌ Error encoding logo: {e}")
            return False
    else:
        print("❌ Logo not found in any of these locations:")
        print("   - ./logo.png (project root)")
        print("   - ./static/logo.png")
        print("   - ./assets/logo.png")
        print("   - ../ (parent directory)")
        
        print("\nPlease place your 'logo.png' file in one of these locations.")
        return False

if __name__ == "__main__":
    success = test_logo_loading()
    sys.exit(0 if success else 1)