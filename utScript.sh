#!/bin/bash

echo "UTSCRIPT - Run OCR Unit Tests!!!"

echo "starting pytest"

/var/lib/jenkins/.local/bin/coverage run -m pytest tests/functional/analytics_tests.py

echo "Testing Finished"

echo "getting coverage report"

/var/lib/jenkins/.local/bin/coverage report -m

/var/lib/jenkins/.local/bin/coverage xml

echo "coverage to be found in coverage.xml file !!!"


