#!/bin/bash

# Pre-Deployment Verification Script

# Run this BEFORE pushing to ensure everything is ready

set -e  # Exit on any error

echo “============================================”
echo “TIF Library Pre-Deployment Verification”
echo “============================================”
echo “”

# Check if in birth-protocol directory

if [ ! -f “docs/TIF_SPEC.md” ]; then
echo “❌ Error: Not in birth-protocol directory”
echo “Please run from repository root”
exit 1
fi

echo “📁 Repository: ✓”
echo “”

# Check required files exist

echo “Checking required files…”
required_files=(
“setup.py”
“requirements.txt”
“tif/**init**.py”
“tif/core.py”
“tif/embeddings.py”
“tif/entropy.py”
“tif/reputation.py”
“tif/thresholds.py”
“tif/utils.py”
“tif/tests/test_core.py”
“tif/tests/test_reputation.py”
“tif/tests/test_thresholds.py”
“examples/basic_usage.py”
)

missing_files=0
for file in “${required_files[@]}”; do
if [ -f “$file” ]; then
echo “  ✓ $file”
else
echo “  ❌ MISSING: $file”
missing_files=$((missing_files + 1))
fi
done

if [ $missing_files -gt 0 ]; then
echo “”
echo “❌ $missing_files file(s) missing!”
echo “Please add all required files before deployment.”
exit 1
fi

echo “”
echo “📦 All files present: ✓”
echo “”

# Test installation

echo “Testing pip installation…”
pip install -e . > /dev/null 2>&1
if [ $? -eq 0 ]; then
echo “  ✓ pip install -e . successful”
else
echo “  ❌ pip install failed”
exit 1
fi

echo “”

# Test imports

echo “Testing imports…”
python -c “from tif.core import directed_information, semantic_distortion” 2>/dev/null
if [ $? -eq 0 ]; then
echo “  ✓ Core functions import successfully”
else
echo “  ❌ Import failed”
exit 1
fi

python -c “from tif.reputation import ReputationTracker” 2>/dev/null
if [ $? -eq 0 ]; then
echo “  ✓ ReputationTracker imports successfully”
else
echo “  ❌ Import failed”
exit 1
fi

python -c “from tif.thresholds import DriftMonitor” 2>/dev/null
if [ $? -eq 0 ]; then
echo “  ✓ DriftMonitor imports successfully”
else
echo “  ❌ Import failed”
exit 1
fi

echo “”

# Run tests if pytest available

if command -v pytest &> /dev/null; then
echo “Running tests…”
pytest tif/tests/ -v –tb=short 2>&1 | tail -10
if [ ${PIPESTATUS[0]} -eq 0 ]; then
echo “  ✓ All tests passed”
else
echo “  ⚠️  Some tests failed (check output above)”
fi
else
echo “⚠️  pytest not installed - skipping tests”
fi

echo “”
echo “============================================”
echo “✅ TIF Library Ready for Deployment!”
echo “============================================”
echo “”
echo “Next steps:”
echo “1. git checkout -b feat/tif-library-v0.1.0”
echo “2. git add tif/ setup.py requirements.txt examples/ *.md”
echo “3. git commit -m ‘feat: Implement complete TIF library v0.1.0’”
echo “4. git push origin feat/tif-library-v0.1.0”
echo “5. Create Pull Request on GitHub”
echo “”
echo “After merge, your command will work:”
echo “git clone https://github.com/waybarek/birth-protocol.git && \”
echo “cd birth-protocol && \”
echo “pip install -e . && \”
echo “python -c "from tif.core import directed_information, semantic_distortion; print(‘TIF v0.1.0 LIVE @waybarek Nov 10 2025 04:48 PM EST’)"”
