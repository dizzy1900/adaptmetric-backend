#!/bin/bash
# Example: How a Cloud Agent would use headless_runner.py
# This script demonstrates typical agent workflows

set -e  # Exit on error

PYTHON=".venv/bin/python"
RUNNER="headless_runner.py"

echo "=== AdaptMetric Cloud Agent Example ==="
echo ""

# Example 1: Simple agriculture analysis
echo "1. Running agriculture analysis for New York..."
$PYTHON $RUNNER \
  --lat 40.7 \
  --lon -74.0 \
  --scenario_year 2050 \
  --project_type agriculture \
  --crop_type maize \
  --temp_delta 2.0 \
  --rain_pct_change -10.0 \
  > /tmp/agriculture_result.json

echo "✓ Results saved to /tmp/agriculture_result.json"
echo "  NPV: $(cat /tmp/agriculture_result.json | python3 -c 'import sys, json; print(json.load(sys.stdin)["financial_analysis"]["npv_usd"])')"
echo ""

# Example 2: Compare multiple temperature scenarios
echo "2. Comparing temperature scenarios (1°C, 2°C, 3°C)..."
for temp in 1.0 2.0 3.0; do
  $PYTHON $RUNNER \
    --lat -2.5 \
    --lon 28.8 \
    --scenario_year 2050 \
    --project_type agriculture \
    --crop_type cocoa \
    --temp_delta $temp \
    --rain_pct_change -15.0 \
    > "/tmp/cocoa_temp_${temp}.json"
  
  yield=$(cat "/tmp/cocoa_temp_${temp}.json" | python3 -c 'import sys, json; print(json.load(sys.stdin)["crop_analysis"]["resilient_yield_pct"])')
  echo "  Temp +${temp}°C: Resilient yield = ${yield}%"
done
echo ""

# Example 3: Health impact assessment
echo "3. Running health impact analysis for West Africa..."
$PYTHON $RUNNER \
  --lat 13.5 \
  --lon 2.1 \
  --scenario_year 2050 \
  --project_type health \
  --workforce_size 250 \
  --daily_wage 12.0 \
  > /tmp/health_result.json 2>/dev/null

echo "✓ Results saved to /tmp/health_result.json"
annual_loss=$(cat /tmp/health_result.json | python3 -c 'import sys, json; print(json.load(sys.stdin)["economic_impact"]["total_economic_impact"]["annual_loss"])')
echo "  Annual economic loss: \$${annual_loss}"
echo ""

# Example 4: Error handling
echo "4. Demonstrating error handling..."
if $PYTHON $RUNNER \
  --lat 999 \
  --lon -74.0 \
  --scenario_year 2050 \
  --project_type agriculture \
  > /tmp/error_result.json 2>&1; then
  echo "✓ Unexpected success"
else
  echo "✗ Expected error caught:"
  cat /tmp/error_result.json | python3 -c 'import sys, json; r=json.load(sys.stdin); print(f"  {r[\"error\"]}: {r[\"message\"]}")'
fi
echo ""

echo "=== All examples complete! ==="
echo "Results saved to /tmp/"
echo ""
echo "Agent Integration Tips:"
echo "• Parse JSON with jq or Python's json module"
echo "• Check 'success' field to detect errors"
echo "• Exit code 0 = success, 1 = error"
echo "• Redirect stderr to hide GEE warnings: 2>/dev/null"
