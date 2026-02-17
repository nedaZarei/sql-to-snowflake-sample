#!/usr/bin/env bash
#
# Run the full dbt fund analytics pipeline.
# Usage: ./run_pipeline.sh [--full-refresh]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

FULL_REFRESH=""
if [[ "${1:-}" == "--full-refresh" ]]; then
    FULL_REFRESH="--full-refresh"
fi

echo "=== dbt Fund Analytics Pipeline ==="
echo "Working directory: $(pwd)"
echo "Started at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# Step 1: Install dependencies
echo "--- Installing dbt packages ---"
dbt deps

# Step 2: Seed raw data
echo ""
echo "--- Seeding raw data ---"
dbt seed $FULL_REFRESH

# Step 3: Check source freshness
echo ""
echo "--- Checking source freshness ---"
dbt source freshness || echo "WARNING: Source freshness check failed (continuing anyway)"

# Step 4: Run all models sequentially
# Anti-pattern: should run independent pipelines in parallel
echo ""
echo "--- Running Pipeline A (Simple) ---"
dbt run --select tag:pipeline_a $FULL_REFRESH

echo ""
echo "--- Running Pipeline B (Medium) ---"
dbt run --select tag:pipeline_b $FULL_REFRESH

echo ""
echo "--- Running Pipeline C (Complex) ---"
dbt run --select tag:pipeline_c $FULL_REFRESH

# Step 5: Run tests
# Anti-pattern: runs all tests at end instead of per-pipeline
echo ""
echo "--- Running tests ---"
dbt test

echo ""
echo "=== Pipeline complete ==="
echo "Finished at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
