#!/bin/bash

if [ "$0" = "$BASH_SOURCE" ]; then
  echo "This script is only for sourcing, exiting..."
  exit
fi


ENV="prd"
ACCOUNT_NUMBER="598619258634"
SUBNETS="subnet-02f4ee7c272d7e664,subnet-030c65e63a92fcb86"
SECURITY_GROUPS="sg-079a8cbff819173ef"
TASK_DEFINITION_NAME=uai3046767-ocr-taskdef-prd
DESIRED_COUNT=1
