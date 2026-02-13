"""
Google Earth Engine Credentials Manager
========================================

Supports multiple credential loading methods with priority fallback:
1. Warp Secrets (for Cloud Agents) - WARP_GEE_CREDENTIALS
2. Environment variable - GEE_SERVICE_ACCOUNT_JSON
3. Local file - credentials.json (project root or ~/.adaptmetric/)
4. Mock mode - Use mock data (no credentials needed)

Usage:
    from gee_credentials import load_gee_credentials, is_gee_available
    
    # Check if GEE is available
    if is_gee_available():
        credentials = load_gee_credentials()
        # Use credentials...
    else:
        # Fall back to mock data
        from mock_data import get_mock_weather
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict


def load_gee_credentials() -> Optional[Dict]:
    """
    Load Google Earth Engine credentials from multiple sources with priority fallback.
    
    Priority order:
    1. WARP_GEE_CREDENTIALS environment variable (Cloud Agents)
    2. GEE_SERVICE_ACCOUNT_JSON environment variable (legacy)
    3. credentials.json in project root
    4. credentials.json in ~/.adaptmetric/
    
    Returns:
        Dictionary with GEE service account credentials or None if not found
    """
    # Priority 1: Warp Secrets (Cloud Agents)
    warp_creds = os.environ.get('WARP_GEE_CREDENTIALS')
    if warp_creds:
        try:
            return json.loads(warp_creds)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse WARP_GEE_CREDENTIALS: {e}")
    
    # Priority 2: Legacy environment variable
    env_creds = os.environ.get('GEE_SERVICE_ACCOUNT_JSON')
    if env_creds:
        try:
            return json.loads(env_creds)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse GEE_SERVICE_ACCOUNT_JSON: {e}")
    
    # Priority 3: credentials.json in project root
    project_creds_path = Path(__file__).parent / 'credentials.json'
    if project_creds_path.exists():
        try:
            with open(project_creds_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to read {project_creds_path}: {e}")
    
    # Priority 4: credentials.json in ~/.adaptmetric/
    home_creds_path = Path.home() / '.adaptmetric' / 'credentials.json'
    if home_creds_path.exists():
        try:
            with open(home_creds_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to read {home_creds_path}: {e}")
    
    # No credentials found
    return None


def is_gee_available() -> bool:
    """
    Check if Google Earth Engine credentials are available.
    
    Returns:
        True if credentials found, False otherwise
    """
    return load_gee_credentials() is not None


def get_credential_source() -> str:
    """
    Get the source of the currently loaded credentials.
    
    Returns:
        String describing the credential source or 'none' if not found
    """
    # Check in priority order
    if os.environ.get('WARP_GEE_CREDENTIALS'):
        return 'warp_secret'
    
    if os.environ.get('GEE_SERVICE_ACCOUNT_JSON'):
        return 'environment_variable'
    
    project_creds_path = Path(__file__).parent / 'credentials.json'
    if project_creds_path.exists():
        return 'project_file'
    
    home_creds_path = Path.home() / '.adaptmetric' / 'credentials.json'
    if home_creds_path.exists():
        return 'home_directory'
    
    return 'none'


def save_credentials_to_home(credentials_dict: Dict) -> Path:
    """
    Save credentials to ~/.adaptmetric/credentials.json for persistent use.
    
    Args:
        credentials_dict: GEE service account credentials dictionary
    
    Returns:
        Path to saved credentials file
    """
    home_dir = Path.home() / '.adaptmetric'
    home_dir.mkdir(parents=True, exist_ok=True)
    
    creds_path = home_dir / 'credentials.json'
    with open(creds_path, 'w') as f:
        json.dump(credentials_dict, f, indent=2)
    
    # Set restrictive permissions (owner read/write only)
    creds_path.chmod(0o600)
    
    return creds_path


def print_credential_status():
    """Print the current credential configuration status."""
    source = get_credential_source()
    available = is_gee_available()
    
    print("=== Google Earth Engine Credentials Status ===")
    print(f"Available: {available}")
    print(f"Source: {source}")
    print("")
    
    if not available:
        print("No credentials found. Options:")
        print("1. Set WARP_GEE_CREDENTIALS environment variable (Cloud Agents)")
        print("2. Set GEE_SERVICE_ACCOUNT_JSON environment variable")
        print("3. Place credentials.json in project root")
        print("4. Place credentials.json in ~/.adaptmetric/")
        print("5. Use --use-mock-data flag for testing without credentials")
    else:
        print(f"Credentials loaded successfully from: {source}")
        
        # Show which methods would work
        print("")
        print("Priority order (highest to lowest):")
        print(f"  1. WARP_GEE_CREDENTIALS: {'✓' if os.environ.get('WARP_GEE_CREDENTIALS') else '✗'}")
        print(f"  2. GEE_SERVICE_ACCOUNT_JSON: {'✓' if os.environ.get('GEE_SERVICE_ACCOUNT_JSON') else '✗'}")
        
        project_path = Path(__file__).parent / 'credentials.json'
        print(f"  3. credentials.json (project): {'✓' if project_path.exists() else '✗'}")
        
        home_path = Path.home() / '.adaptmetric' / 'credentials.json'
        print(f"  4. credentials.json (home): {'✓' if home_path.exists() else '✗'}")


# Example usage and testing
if __name__ == '__main__':
    print_credential_status()
