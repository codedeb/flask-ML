#!/bin/bash

echo "BUILD SCRIPT !!! "
echo "collecting packages"

# /usr/local/bin/pip3 install -r requirements.txt
# git clone --depth 1 --branch v0.1 https://github.com/facebookresearch/detectron2.git
# /usr/local/bin/pip3 install -U detectron2/.   
# /usr/local/bin/pip3 install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"


/usr/local/bin/pip3 install -r trequirements.txt

echo "package collection done!!!"

echo "UTSCRIPT - Run OCR Unit Tests!!!"

echo "starting pytest"


coverage run -m pytest tests/functional/analytics_tests.py

echo "Testing Finished"

echo "getting coverage report"

coverage report -m

coverage xml

echo "coverage to be found in coverage.xml file !!!"
