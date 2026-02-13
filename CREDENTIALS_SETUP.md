# Google Earth Engine Credentials Setup

## Overview

The adaptmetric-backend supports multiple ways to provide Google Earth Engine (GEE) credentials with automatic fallback priority. This ensures maximum flexibility for local development, Cloud Agents, and production deployments.

## Credential Priority Order

The system checks for credentials in this order (first found wins):

1. **WARP_GEE_CREDENTIALS** environment variable (Cloud Agents) ⭐ Recommended for Factory
2. **GEE_SERVICE_ACCOUNT_JSON** environment variable (Legacy)
3. **credentials.json** in project root
4. **credentials.json** in `~/.adaptmetric/` directory
5. **Mock data mode** (testing only, no credentials needed)

## Setup Methods

### Method 1: Warp Secrets (Cloud Agents) ⭐ Recommended

**For Factory Cloud Agent environments:**

1. Get your GEE service account credentials JSON
2. Add as a Warp Secret in Factory:
   ```bash
   # In Factory Warp settings, add secret:
   Name: WARP_GEE_CREDENTIALS
   Value: <paste entire credentials.json content>
   ```

3. Cloud Agents will automatically use this secret

**Advantages:**
- ✓ Secure (never in code or repo)
- ✓ Automatic in Cloud Agent environments
- ✓ Easy to rotate credentials
- ✓ Works across all Factory projects

### Method 2: Environment Variable (Legacy)

**For local development or traditional deployments:**

```bash
# Export as environment variable
export GEE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"...",...}'

# Or add to .bashrc / .zshrc
echo 'export GEE_SERVICE_ACCOUNT_JSON="..."' >> ~/.bashrc
source ~/.bashrc
```

**Advantages:**
- ✓ Works with existing setups
- ✓ No file needed

**Disadvantages:**
- ⚠️ Easy to accidentally expose in logs
- ⚠️ Must be set in every shell

### Method 3: Project File (Not Recommended)

**Place credentials.json in project root:**

```bash
cd adaptmetric-backend
cp /path/to/your/credentials.json .
```

**⚠️ IMPORTANT:** This file is in `.gitignore` and will NOT be committed to the repo.

**Advantages:**
- ✓ Simple for local development
- ✓ No environment variables needed

**Disadvantages:**
- ⚠️ Risk of accidental commit if .gitignore removed
- ⚠️ Not suitable for shared environments

### Method 4: Home Directory (Recommended for Local Dev)

**Place credentials in your home directory:**

```bash
mkdir -p ~/.adaptmetric
cp /path/to/your/credentials.json ~/.adaptmetric/
chmod 600 ~/.adaptmetric/credentials.json
```

**Advantages:**
- ✓ Secure (outside project directory)
- ✓ Can't be accidentally committed
- ✓ Works across all your projects
- ✓ Persistent across git operations

**Disadvantages:**
- ⚠️ Manual setup required

### Method 5: Mock Data Mode (Testing)

**No credentials needed for testing:**

```bash
python headless_runner.py \
  --lat 40.7 --lon -74.0 \
  --scenario_year 2050 \
  --project_type agriculture \
  --use-mock-data
```

**Advantages:**
- ✓ No credentials needed
- ✓ Perfect for testing
- ✓ Unlimited runs (no API limits)
- ✓ Fast (<0.1s response)

**Disadvantages:**
- ⚠️ Not real GEE data
- ⚠️ Not suitable for production analysis

## Getting GEE Service Account Credentials

If you don't have GEE credentials yet:

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create/Select Project:**
   - Create a new project or select existing one
   - Note the project ID

3. **Enable Earth Engine API:**
   - Go to "APIs & Services" > "Library"
   - Search for "Earth Engine API"
   - Click "Enable"

4. **Create Service Account:**
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `adaptmetric-gee`
   - Role: "Earth Engine Resource Admin"

5. **Generate Key:**
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the JSON file (this is your credentials.json)

6. **Register with Earth Engine:**
   - Visit: https://signup.earthengine.google.com/
   - Register your service account email (found in the JSON)
   - Wait for approval (usually instant)

## Checking Credential Status

Run the credential checker:

```bash
cd adaptmetric-backend
python gee_credentials.py
```

**Example output (credentials found):**
```
=== Google Earth Engine Credentials Status ===
Available: True
Source: warp_secret

Credentials loaded successfully from: warp_secret

Priority order (highest to lowest):
  1. WARP_GEE_CREDENTIALS: ✓
  2. GEE_SERVICE_ACCOUNT_JSON: ✗
  3. credentials.json (project): ✗
  4. credentials.json (home): ✗
```

**Example output (no credentials):**
```
=== Google Earth Engine Credentials Status ===
Available: False
Source: none

No credentials found. Options:
1. Set WARP_GEE_CREDENTIALS environment variable (Cloud Agents)
2. Set GEE_SERVICE_ACCOUNT_JSON environment variable
3. Place credentials.json in project root
4. Place credentials.json in ~/.adaptmetric/
5. Use --use-mock-data flag for testing without credentials
```

## Testing Credentials

### Test with Python

```python
from gee_credentials import is_gee_available, get_credential_source

if is_gee_available():
    print(f"✓ Credentials loaded from: {get_credential_source()}")
else:
    print("✗ No credentials found")
```

### Test with Headless Runner

```bash
# Test with real GEE (requires credentials)
python headless_runner.py \
  --lat 40.7 --lon -74.0 \
  --scenario_year 2050 \
  --project_type agriculture

# Test with mock data (no credentials needed)
python headless_runner.py \
  --lat 40.7 --lon -74.0 \
  --scenario_year 2050 \
  --project_type agriculture \
  --use-mock-data
```

## Security Best Practices

### ✓ DO:
- Use Warp Secrets for Cloud Agents
- Store in `~/.adaptmetric/` for local development
- Set file permissions: `chmod 600 credentials.json`
- Rotate credentials regularly
- Use mock data for testing

### ✗ DON'T:
- Commit credentials.json to git
- Share credentials via email or chat
- Store in public cloud storage
- Log credential contents
- Use in public demos (use mock data instead)

## Troubleshooting

### Issue: "GEE credentials not found"

**Solutions:**
1. Check credential status: `python gee_credentials.py`
2. Verify file exists: `ls -la ~/.adaptmetric/credentials.json`
3. Check environment variable: `echo $WARP_GEE_CREDENTIALS`
4. Use mock data: Add `--use-mock-data` flag

### Issue: "ServiceAccountCredentials" error

**Cause:** Credentials JSON is malformed

**Solutions:**
1. Validate JSON: `cat credentials.json | python -m json.tool`
2. Re-download from Google Cloud Console
3. Check for extra characters or quotes

### Issue: "Earth Engine initialization failed"

**Cause:** Service account not registered with Earth Engine

**Solutions:**
1. Register at: https://signup.earthengine.google.com/
2. Use the service account email from credentials.json
3. Wait a few minutes for approval

### Issue: Credentials work locally but not in Cloud Agent

**Cause:** Warp Secret not configured

**Solutions:**
1. Add WARP_GEE_CREDENTIALS in Factory Warp settings
2. Ensure entire JSON is copied (including braces)
3. Check secret name spelling

## For Cloud Agent Environments

### Recommended Setup

**In Factory Warp:**
```
Secret Name: WARP_GEE_CREDENTIALS
Secret Value: {
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "adaptmetric-gee@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### Testing in Cloud Agent

```bash
# Cloud Agent will automatically use WARP_GEE_CREDENTIALS
python headless_runner.py \
  --lat 40.7 --lon -74.0 \
  --scenario_year 2050 \
  --project_type agriculture

# Check which credential source is used
python gee_credentials.py
```

### Fallback to Mock Data

If credentials fail in Cloud Agent, use mock data:

```bash
python headless_runner.py [...] --use-mock-data
```

## Credential File Format

Your `credentials.json` should look like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "adaptmetric-gee@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/adaptmetric-gee%40your-project.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

## Summary

**For Cloud Agents (Factory):**
- Use `WARP_GEE_CREDENTIALS` secret ⭐

**For Local Development:**
- Use `~/.adaptmetric/credentials.json` 🏠

**For Testing:**
- Use `--use-mock-data` flag 🧪

**Never commit credentials to git!** 🚫

---

**Last Updated:** 2026-02-13  
**Version:** 1.0.0
