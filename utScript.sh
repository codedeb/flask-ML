#!/bin/bash
echo "UTSCRIPT - Run OCR Unit Tests!!!"

echo "set CHROME_BIN"
export CHROME_BIN="/bin/google-chrome"

echo "starting pytest"

pytest  tests/functional/analytics_tests.py
