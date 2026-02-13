#!/bin/bash
# Quick health check for Railway/Render/cloud deployments
# This script verifies the installation succeeded before starting the app

set -e  # Exit on any error

echo "========================================"
echo "AdaptMetric Backend - Installation Check"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python --version || python3 --version
echo ""

# Check critical packages
echo "Checking critical packages..."
python -c "
import sys
try:
    import numpy as np
    import pandas as pd
    import sklearn
    import scipy
    import ee
    import flask
    import flask_cors
    import gunicorn
    
    print(f'✓ numpy:           {np.__version__}')
    print(f'✓ pandas:          {pd.__version__}')
    print(f'✓ scikit-learn:    {sklearn.__version__}')
    print(f'✓ scipy:           {scipy.__version__}')
    print(f'✓ earthengine-api: {ee.__version__}')
    print(f'✓ flask:           {flask.__version__ if hasattr(flask, \"__version__\") else \"3.x\"}')
    print(f'✓ gunicorn:        installed')
    print('')
    print('✓ All critical packages installed!')
    
except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
"

echo ""
echo "========================================"
echo "✓ Installation check passed!"
echo "========================================"
echo ""

# Check if verify_requirements.py exists and run it
if [ -f "verify_requirements.py" ]; then
    echo "Running full verification..."
    python verify_requirements.py
fi

exit 0
