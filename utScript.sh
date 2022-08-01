#!/bin/bash
echo "UTSCRIPT - Run OCR Unit Tests!!!"

echo "starting pytest"


coverage run -m pytest tests/functional/analytics_tests.py

echo "Testing Finished"

echo "getting coverage report"

coverage report -m

coverage xml

echo "coverage to be found in coverage.xml file !!!"


