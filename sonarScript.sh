#!/bin/bash

echo "Run Sonar scanner" 

/usr/local/bin/pip3 install wget

wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.2.0.1873-linux.zip

unzip sonar-scanner-cli-4.2.0.1873-linux.zip

mv sonar-scanner-cli-4.2.0.1873-linux /opt/sonar/



PATH=/opt/sonar/ sonar-scanner-4.2.0.1873-linux/bin

sonar-scanner

echo "Completed SonarScan for OCR"