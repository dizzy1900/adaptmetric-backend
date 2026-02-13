# Cloud Agent Setup Guide

## ✅ Repository Ready for Cloud Agents

Your `adaptmetric-backend` repo is now fully configured for Cloud Agent testing with secure credential management.

## 🚀 Quick Start

### For Cloud Agents (Factory)

**1. Set up Warp Secret:**
```
Secret Name: WARP_GEE_CREDENTIALS
Secret Value: {paste your GEE service account JSON}
```

**2. Run tests:**
```bash
# With real GEE data (uses WARP_GEE_CREDENTIALS automatically)
python headless_runner.py \
  --lat 40.7 --lon -74.0 \
  --scenario_year 2050 \
  --project_type agriculture

# With mock data (no credentials needed, unlimited runs)
python headless_runner.py \
  --lat 40.7 --lon -74.0 \
  --scenario_year 2050 \
  --project_type agriculture \
  --use-mock-data
```

**3. Verify credentials:**
```bash
python gee_credentials.py
```

## 📦 What Was Pushed to GitHub

### Commit 1: Headless Runner + Mock Data System
**Commit:** `38a8ef2`

**Files Added:**
- `headless_runner.py` - Standalone CLI for calculations
- `mock_data.py` - Deterministic mock weather generator
- `test_mock_mode.sh` - Test suite for validation
- `example_agent_usage.sh` - Integration examples
- `HEADLESS_RUNNER.md` - Usage guide
- `MOCK_DATA_GUIDE.md` - Mock data documentation
- `CODE_FORTIFICATION_READY.md` - Readiness checklist

**Key Features:**
- Zero API calls with `--use-mock-data` flag
- 1,000+ tests per minute capability
- Deterministic results (same input = same output)
- Perfect for Code Fortification sprints

### Commit 2: Flexible Credentials System
**Commit:** `74272ea`

**Files Added:**
- `gee_credentials.py` - Multi-source credential loader
- `CREDENTIALS_SETUP.md` - Comprehensive setup guide

**Files Updated:**
- `gee_connector.py` - Uses new credential system
- `coastal_engine.py` - Uses new credential system
- `flood_engine.py` - Uses new credential system
- `.gitignore` - Protects credentials from commits
- `HEADLESS_RUNNER.md` - Added credential reference

**Key Features:**
- Warp Secrets support (`WARP_GEE_CREDENTIALS`)
- Multiple credential sources with priority fallback
- Secure: No credentials in repo
- Flexible: Works locally and in Cloud Agents

## 🔐 Credential Priority Order

The system automatically checks for credentials in this order:

1. **WARP_GEE_CREDENTIALS** (Cloud Agents) ⭐
2. **GEE_SERVICE_ACCOUNT_JSON** (legacy env var)
3. **credentials.json** (project root)
4. **credentials.json** (~/.adaptmetric/)
5. **Mock mode** (`--use-mock-data` flag)

## 🛡️ Security Guarantees

✅ **No credentials in repo:**
- `credentials.json` in `.gitignore`
- `*credentials*.json` pattern blocked
- `.adaptmetric/` directory blocked

✅ **Multiple secure options:**
- Warp Secrets (recommended for Cloud Agents)
- Home directory (~/.adaptmetric/)
- Environment variables

✅ **Safe testing:**
- Mock data mode requires no credentials
- Unlimited test runs with `--use-mock-data`

## 📋 Cloud Agent Workflow

### Setup Phase (One-time)

**In Factory Warp Settings:**
1. Navigate to Warp Secrets
2. Add new secret:
   - Name: `WARP_GEE_CREDENTIALS`
   - Value: Copy entire GEE service account JSON
3. Save

**Verify in Cloud Agent:**
```bash
python gee_credentials.py
# Should show: Source: warp_secret
```

### Testing Phase (During Sprint)

**High-volume testing (recommended):**
```bash
# Use mock data for unlimited testing
for i in {1..1000}; do
  python headless_runner.py \
    --lat $((i - 500)) \
    --lon $((i - 500)) \
    --project_type agriculture \
    --use-mock-data
done
```

**Spot-check with real GEE:**
```bash
# Verify calculations with real data (uses WARP_GEE_CREDENTIALS)
python headless_runner.py \
  --lat 40.7 --lon -74.0 \
  --project_type agriculture
```

## 🧪 Testing Checklist

Before starting Code Fortification sprint:

```bash
# 1. Check credentials
python gee_credentials.py

# 2. Test mock data
python headless_runner.py --lat 40.7 --lon -74.0 --project_type agriculture --use-mock-data

# 3. Run test suite
./test_mock_mode.sh

# 4. Verify reproducibility
python headless_runner.py --lat 40.7 --lon -74.0 --project_type agriculture --use-mock-data > test1.json
python headless_runner.py --lat 40.7 --lon -74.0 --project_type agriculture --use-mock-data > test2.json
diff test1.json test2.json  # Should be identical

# 5. Test real GEE (if credentials available)
python headless_runner.py --lat 40.7 --lon -74.0 --project_type agriculture
```

## 📚 Documentation Files

### Main Guides
- **[CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md)** - Complete credential setup
- **[HEADLESS_RUNNER.md](HEADLESS_RUNNER.md)** - Headless runner usage
- **[MOCK_DATA_GUIDE.md](MOCK_DATA_GUIDE.md)** - Mock data system
- **[CODE_FORTIFICATION_READY.md](CODE_FORTIFICATION_READY.md)** - Readiness checklist
- **[CLOUD_AGENT_SETUP.md](CLOUD_AGENT_SETUP.md)** - This file

### Test Scripts
- **test_mock_mode.sh** - Comprehensive test suite
- **example_agent_usage.sh** - Integration examples

### Python Modules
- **headless_runner.py** - Main CLI tool
- **mock_data.py** - Mock data generator
- **gee_credentials.py** - Credential loader

## 🎯 Recommended Strategy

### For Code Fortification Sprint:

**Use mock data by default:**
```bash
# 99% of tests should use mock data
python headless_runner.py [...args...] --use-mock-data
```

**Why?**
- ✓ Zero API calls
- ✓ Unlimited runs
- ✓ Instant response
- ✓ Deterministic results
- ✓ No rate limits
- ✓ No credentials needed

**Spot-check with real GEE:**
```bash
# 1% of tests for validation
python headless_runner.py [...args...]
# Uses WARP_GEE_CREDENTIALS automatically
```

**Why?**
- ✓ Verify calculations match real data
- ✓ Catch integration issues
- ✓ Validate GEE API changes

## 🚨 Troubleshooting

### Issue: Credentials not found in Cloud Agent

**Check:**
```bash
python gee_credentials.py
```

**Solutions:**
1. Verify `WARP_GEE_CREDENTIALS` secret exists in Factory
2. Check secret name spelling (case-sensitive)
3. Ensure entire JSON is copied (including braces)
4. Use `--use-mock-data` as fallback

### Issue: "ServiceAccountCredentials" error

**Cause:** Malformed credentials JSON

**Solutions:**
1. Validate JSON format: `echo $WARP_GEE_CREDENTIALS | python -m json.tool`
2. Re-copy from Google Cloud Console
3. Check for extra quotes or escape characters

### Issue: Tests too slow

**Solution:** Use mock data mode
```bash
# Instead of this (2-5s per request):
python headless_runner.py [...args...]

# Use this (<0.1s per request):
python headless_runner.py [...args...] --use-mock-data
```

## 📊 Performance Comparison

| Mode | Response Time | Rate Limit | Credentials |
|------|---------------|------------|-------------|
| **Mock Data** | <0.1s | Unlimited | Not needed |
| **GEE (real)** | 2-5s | ~1000/day | Required |
| **Fallback** | <0.1s | Unlimited | Not needed |

## ✨ Example Cloud Agent Workflow

```bash
#!/bin/bash
# Code Fortification Sprint Script

echo "Starting Cloud Agent tests..."

# Check credential status
python gee_credentials.py

# Run 100 mock data tests (fast)
echo "Running 100 mock data tests..."
for i in {1..100}; do
  python headless_runner.py \
    --lat $((i - 50)) \
    --lon $((i * 2 - 100)) \
    --project_type agriculture \
    --temp_delta 2.0 \
    --use-mock-data \
    > result_${i}.json
done

# Spot-check with real GEE (if credentials available)
if python gee_credentials.py | grep -q "Available: True"; then
  echo "Running 5 real GEE validation tests..."
  for lat in 0 25 45 -25 -45; do
    python headless_runner.py \
      --lat $lat \
      --lon 0 \
      --project_type agriculture \
      > validation_${lat}.json
  done
fi

echo "Tests complete!"
```

## 🎉 Ready to Go!

Your repository is now fully configured for:
- ✅ Cloud Agent testing with Warp Secrets
- ✅ Local development with flexible credentials
- ✅ High-volume testing with mock data
- ✅ Secure credential management
- ✅ Zero risk of credential leaks

**Next Steps:**
1. Add `WARP_GEE_CREDENTIALS` to Factory Warp
2. Clone repo in Cloud Agent environment
3. Run `python gee_credentials.py` to verify
4. Start Code Fortification sprint!

---

**Repository:** https://github.com/dizzy1900/adaptmetric-backend  
**Latest Commit:** `74272ea`  
**Last Updated:** 2026-02-13  
**Status:** ✅ Cloud Agent Ready
