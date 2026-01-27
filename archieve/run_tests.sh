#!/bin/bash
set -e

echo "🔎 Running inline self-test..."
python query_engine.py > selftest_output.txt || { echo "❌ Inline self-test failed"; exit 1; }

echo "✅ Inline self-test passed. Output saved to selftest_output.txt."

echo "🔎 Running pytest suite..."
pytest tests/test_query_engine_v165.py -v --maxfail=1 --disable-warnings || {
  echo "❌ Pytest suite failed. Attempting auto-debug..."
  # Cursor: analyze pytest failure logs and apply fixes automatically
  exit 1
}

echo "✅ All tests passed successfully." 