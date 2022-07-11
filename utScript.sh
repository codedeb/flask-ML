#!/bin/bash
echo "UTSCRIPT - Run OCR Unit Tests!!!"

echo "set CHROME_BIN"
export CHROME_BIN="/bin/google-chrome"

echo "start pytest"

pytest api_tests/tests.py
