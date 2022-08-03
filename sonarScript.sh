#!/bin/bash

echo "Run Sonar scanner" 

mkdir sonarscanner -p

cd /sonarscanner

/usr/local/bin/pip3 install wget

wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.2.0.1873-linux.zip

unzip sonar-scanner-cli-4.2.0.1873-linux.zip

rm sonar-scanner-cli-4.2.0.1873-linux.zip

chmod +x sonar-scanner-4.2.0.1873-linux/bin/sonar-scanner

# ln -s sonarscanner/sonar-scanner-4.2.0.1873-linux/bin/sonar-scanner/

sonar-scanner.sh start

echo "Completed SonarScan for OCR"