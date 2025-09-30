"""Test script to verify the restructured RDJAT package works correctly."""

import sys
from pathlib import Path

# Add src to path so we can import the package
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        # Test main package import
        import rdjat
        print("✓ Main package imported successfully")
        
        # Test core modules
        from rdjat.core import embedding, extraction
        print("✓ Core modules imported successfully")
        
        # Test utils modules
        from rdjat.utils import image_processing
        print("✓ Utils modules imported successfully")
        
        # Test GUI module
        from rdjat.gui import interface
        print("✓ GUI module imported successfully")
        
        # Test specific functions
        from rdjat.core.embedding import embed_once, EmbedResult
        from rdjat.core.extraction import extract_with_TRA
        from rdjat.utils.image_processing import load_matlab_image, psnr_uint8
        print("✓ Specific functions imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_package_structure():
    """Test that the package structure is correct."""
    print("\nTesting package structure...")
    
    expected_dirs = [
        "src/rdjat",
        "src/rdjat/core", 
        "src/rdjat/gui",
        "src/rdjat/utils",
        "assets/images",
        "assets/test_data", 
        "examples",
        "tests",
        "docs"
    ]
    
    missing_dirs = []
    for dir_path in expected_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"✗ Missing directories: {missing_dirs}")
        return False
    else:
        print("✓ All expected directories exist")
        return True

def test_assets():
    """Test that assets were moved correctly."""
    print("\nTesting assets...")
    
    images_dir = project_root / "assets" / "images"
    test_data_dir = project_root / "assets" / "test_data"
    examples_dir = project_root / "examples"
    
    # Check for some expected files
    expected_files = [
        images_dir / "Aerial.tiff",
        test_data_dir / "random-binary_1Kb.txt",
        examples_dir / "Batch_Testing.m"
    ]
    
    missing_files = []
    for file_path in expected_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print(f"✗ Missing asset files: {missing_files}")
        return False
    else:
        print("✓ Asset files found in correct locations")
        return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("RDJAT Package Structure Verification")
    print("=" * 50)
    
    tests = [
        test_package_structure,
        test_assets,
        test_imports,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("🎉 All tests passed! The restructured package is working correctly.")
        print("\nYou can now run the application with:")
        print("  python -m src.rdjat")
        print("or after installation with:")
        print("  pip install -e .")
        print("  rdjat")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)