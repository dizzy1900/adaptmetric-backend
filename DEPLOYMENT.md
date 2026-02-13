# Deployment Guide - AdaptMetric Backend

## ✓ Requirements Verified

This project uses **strictly pinned versions** to ensure zero installation failures in cloud environments.

### Key Geospatial Stack
- **earthengine-api 1.7.10** - Google Earth Engine Python API
- **numpy 2.4.1** - Core numerical computing
- **pandas 3.0.0** - Data manipulation
- **scipy 1.17.0** - Scientific computing  
- **scikit-learn 1.8.0** - Machine learning (surrogate models)

All versions tested and verified compatible ✓

## Installation

### Local Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install exact versions (recommended)
pip install -r requirements.txt

# Verify installation
python verify_requirements.py
```

### Cloud Deployment (Railway, Render, Heroku, etc.)

#### Option 1: Standard Install (Recommended)
```bash
pip install -r requirements.txt
```

#### Option 2: Force Exact Versions (If resolver issues occur)
```bash
pip install -r requirements.txt --no-deps
pip check  # Verify no broken dependencies
```

#### Option 3: Manual verification before deployment
```bash
pip install -r requirements.txt
python verify_requirements.py
```

## Environment Variables

Required for production:

```bash
# Google Earth Engine
EARTHENGINE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
EARTHENGINE_PRIVATE_KEY_FILE=path/to/private-key.json
# OR
EARTHENGINE_PRIVATE_KEY=<json-content-as-string>

# Database (if using Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Analytics (optional)
POSTHOG_API_KEY=your-posthog-key

# Flask
FLASK_ENV=production
FLASK_DEBUG=0
```

## Running the Application

### Development
```bash
source .venv/bin/activate
python main.py
```

### Production (with Gunicorn)
```bash
gunicorn main:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

## Compatibility Notes

### Why These Exact Versions?

1. **numpy 2.4.1**: Latest stable with pandas 3.0 support
2. **pandas 3.0.0**: Latest with significant performance improvements
3. **earthengine-api 1.7.10**: Latest with numpy 2.x compatibility
4. **scikit-learn 1.8.0**: Requires numpy>=1.26.0 and scipy>=1.6.0
5. **scipy 1.17.0**: Compatible with numpy 2.4.1 and scikit-learn 1.8.0

### Known Compatibility Matrix

| Package | Requires | Compatible With |
|---------|----------|----------------|
| pandas 3.0.0 | numpy>=1.26.0, <3.0 | ✓ numpy 2.4.1 |
| scikit-learn 1.8.0 | numpy>=1.26.0, scipy>=1.6.0 | ✓ numpy 2.4.1, scipy 1.17.0 |
| earthengine-api 1.7.10 | numpy (flexible) | ✓ numpy 2.4.1 |
| scipy 1.17.0 | numpy>=1.26.0, <2.5 | ✓ numpy 2.4.1 |

## Troubleshooting

### Issue: "No matching distribution found"
**Solution**: Ensure Python 3.12+ is installed. Some packages require newer Python versions.

```bash
python --version  # Should be 3.12+
```

### Issue: Version conflicts during install
**Solution**: Use the `--no-deps` flag to force exact versions:

```bash
pip install -r requirements.txt --no-deps
```

### Issue: Import errors after installation
**Solution**: Run the verification script:

```bash
python verify_requirements.py
```

### Issue: Gunicorn not starting
**Solution**: Check that Flask app is properly named in main.py:

```python
# main.py should have:
app = Flask(__name__)

# At the end:
if __name__ == '__main__':
    app.run()
```

## Testing Before Deployment

Always run these checks before deploying:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify all packages
python verify_requirements.py

# 3. Run basic import test
python -c "import numpy, pandas, sklearn, ee, flask; print('✓ All imports successful')"

# 4. Check for security vulnerabilities (optional)
pip list --outdated
```

## Production Checklist

- [ ] All environment variables set
- [ ] `verify_requirements.py` passes
- [ ] Gunicorn configured correctly
- [ ] Google Earth Engine credentials available
- [ ] Database connection tested
- [ ] CORS settings configured for your domain
- [ ] Logging configured
- [ ] Error handling in place

## Performance Tips

1. **Use Gunicorn workers**: Set to `2 * CPU_CORES + 1`
2. **Increase timeout**: GEE operations can take 60-120s
3. **Enable caching**: Cache GEE results where possible
4. **Monitor memory**: numpy/pandas operations can be memory-intensive

## Support

If deployment fails:
1. Check Python version (3.12+ required)
2. Run `verify_requirements.py` 
3. Check environment variables are set
4. Review application logs for specific errors

---

**Generated**: 2026-02-13  
**Verified Compatible**: ✓ All geospatial libraries tested
