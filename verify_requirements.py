#!/usr/bin/env python3
"""
Verification script for requirements.txt
Tests all critical geospatial and ML library compatibility
Run this after: pip install -r requirements.txt
"""

import sys
import importlib.metadata

def check_version(package, expected):
    """Check if installed version matches expected version"""
    try:
        installed = importlib.metadata.version(package)
        if installed == expected:
            print(f"✓ {package:25s} {installed:15s} [EXACT MATCH]")
            return True
        else:
            print(f"✗ {package:25s} {installed:15s} [EXPECTED: {expected}]")
            return False
    except importlib.metadata.PackageNotFoundError:
        print(f"✗ {package:25s} NOT INSTALLED")
        return False

def test_imports():
    """Test that all critical packages can be imported"""
    print("\n" + "="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    critical_packages = [
        ('numpy', 'np'),
        ('pandas', 'pd'),
        ('sklearn', 'scikit-learn'),
        ('scipy', 'scipy'),
        ('ee', 'earthengine-api'),
        ('flask', 'flask'),
        ('requests', 'requests'),
    ]
    
    all_ok = True
    for module_name, display_name in critical_packages:
        try:
            mod = __import__(module_name)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✓ {display_name:25s} v{version}")
        except ImportError as e:
            print(f"✗ {display_name:25s} IMPORT FAILED: {e}")
            all_ok = False
    
    return all_ok

def test_compatibility():
    """Test compatibility between key libraries"""
    print("\n" + "="*60)
    print("TESTING COMPATIBILITY")
    print("="*60)
    
    all_ok = True
    
    try:
        import numpy as np
        import pandas as pd
        
        # Test numpy + pandas
        df = pd.DataFrame({'test': np.array([1, 2, 3])})
        print(f"✓ numpy {np.__version__} + pandas {pd.__version__}")
    except Exception as e:
        print(f"✗ numpy + pandas compatibility: {e}")
        all_ok = False
    
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        
        # Test numpy + scikit-learn
        model = RandomForestRegressor(n_estimators=2, random_state=42)
        X = np.array([[1, 2], [3, 4]])
        y = np.array([1, 2])
        model.fit(X, y)
        pred = model.predict(X)
        
        import sklearn
        print(f"✓ numpy {np.__version__} + scikit-learn {sklearn.__version__}")
    except Exception as e:
        print(f"✗ numpy + scikit-learn compatibility: {e}")
        all_ok = False
    
    try:
        import scipy
        from scipy import stats
        
        # Test scipy
        result = stats.norm.rvs(size=10, random_state=42)
        print(f"✓ scipy {scipy.__version__}")
    except Exception as e:
        print(f"✗ scipy compatibility: {e}")
        all_ok = False
    
    try:
        import ee
        
        # Test earthengine-api (don't initialize, just import)
        print(f"✓ earthengine-api {ee.__version__}")
    except Exception as e:
        print(f"✗ earthengine-api compatibility: {e}")
        all_ok = False
    
    return all_ok

def main():
    """Run all verification checks"""
    print("="*60)
    print("REQUIREMENTS.TXT VERIFICATION")
    print("="*60)
    
    # Critical versions to check
    critical_versions = {
        'numpy': '2.4.1',
        'pandas': '3.0.0',
        'scikit-learn': '1.8.0',
        'scipy': '1.17.0',
        'earthengine-api': '1.7.10',
        'Flask': '3.1.2',
        'flask-cors': '6.0.2',
        'gunicorn': '24.1.1',
        'requests': '2.32.5',
        'posthog': '7.6.0',
        'python-dotenv': '1.2.1',
    }
    
    print("\nCHECKING CRITICAL PACKAGE VERSIONS:")
    print("-" * 60)
    
    all_versions_ok = all(
        check_version(pkg, ver) for pkg, ver in critical_versions.items()
    )
    
    imports_ok = test_imports()
    compat_ok = test_compatibility()
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"Version Check:     {'PASS ✓' if all_versions_ok else 'FAIL ✗'}")
    print(f"Import Test:       {'PASS ✓' if imports_ok else 'FAIL ✗'}")
    print(f"Compatibility:     {'PASS ✓' if compat_ok else 'FAIL ✗'}")
    print("="*60)
    
    if all_versions_ok and imports_ok and compat_ok:
        print("\n✓ ALL CHECKS PASSED - Ready for cloud deployment!")
        return 0
    else:
        print("\n✗ SOME CHECKS FAILED - Review errors above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
