#!/bin/bash

echo "BUILD SCRIPT !!! "
echo "collecting packages"

pip install -r requirements.txt 
git clone --depth 1 --branch v0.1 https://github.com/facebookresearch/detectron2.git
pip install -U detectron2
pip install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"



echo "package collection done!!!"
