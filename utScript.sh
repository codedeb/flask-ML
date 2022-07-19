#!/bin/bash
echo "UTSCRIPT - Run OCR Unit Tests!!!"

echo "set CHROME_BIN"
export CHROME_BIN="/bin/google-chrome"
echo "starting pytest"

#pip3 install pytest
python -m pytest tests/functional/analytics_tests.py

echo "Testing ends!!!"
