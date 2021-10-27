#!/bin/bash

if [ "$0" = "$BASH_SOURCE" ]; then
  echo "This script is only for sourcing, exiting..."
  exit
fi


ENV="qa"
ACCOUNT_NUMBER="598619258634"
SUBNETS="subnet-00a2cc8eb8b597505,subnet-076fbc33b8e7fc094"
SECURITY_GROUPS="sg-0b09ac22f702c06fd"
TASK_DEFINITION_NAME=uai3046767-ocr-taskdef-qa
