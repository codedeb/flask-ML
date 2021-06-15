#!/bin/bash

imageName='plp-cpl-ocr-service'
BUILD_VERSION="latest"
echo "BUILD Version is ${BUILD_VERSION}"

docker build -t $imageName:latest . --no-cache
docker tag "$imageName":latest registry.gear.ge.com/pwr-plp-dib/"$imageName":"$BUILD_VERSION"
docker push registry.gear.ge.com/pwr-plp-dib/"$imageName":"$BUILD_VERSION"
#docker push registry.gear.ge.com/pwr-plp-dib/"$imageName":latest

echo "setting BanzaiUserData.json for GitOps:"
jq --arg APPVERSION "$BUILD_VERSION" '.gitOps.versions."plp-cpl-ocr-service".version = $APPVERSION' gitOps.json > BanzaiUserData.json
cat BanzaiUserData.json
