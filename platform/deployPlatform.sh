#!/bin/bash

CURRENT_TIME=$(date +%Y%m%d%H%M%S)
export CURRENT_TIME=$CURRENT_TIME

CURRENT_DIR=$(dirname "$0")
REPO_DIR="$CURRENT_DIR/."

if [ "$1" = "dev" ]; then
  source $CURRENT_DIR/dev/deploy-variables.sh
elif [ "$1" = "qa" ]; then
  source $CURRENT_DIR/stg/deploy-variables.sh
elif [ "$1" = "prod" ]; then
  source $CURRENT_DIR/prd/deploy-variables.sh
else
  echo "Usage: $0 dev/qa/prod"
  exit 1
fi

# If we are doing a Jenkins build, log in to ECR
if [ ! -n "${JENKINS_HOME+1}" ]; then
  $(aws ecr get-login --no-include-email --region us-east-1 --no-verify-ssl)
fi

###########################################################
### LOG IN TO PRISMA CLOUD
###########################################################
# Need to capture the output here
PRISMA_USERNAME=$(aws secretsmanager get-secret-value --secret-id /uai3046767/cpl/dev/Common --region us-east-1 --no-verify-ssl --query "SecretString" | jq -r fromjson.PrismaAccessKeyID)
PRISMA_PASSWORD=$(aws secretsmanager get-secret-value --secret-id /uai3046767/cpl/dev/Common --region us-east-1 --no-verify-ssl --query "SecretString" | jq -r fromjson.PrismaSecretKey)
TOKEN=$(curl -k -X POST \
  https://us-east1.cloud.twistlock.com/us-2-158286731/api/v1/authenticate \
  -H "Content-Type: application/json" \
  -d '{"username": "'${PRISMA_USERNAME}'", "password": "'${PRISMA_PASSWORD}'"}' \
  | jq -r .token)
  
  echo "LOG IN TO PRISMA CLOUD..."

if [[ -z $TOKEN ]]; then
  echo "Error, exiting deploy script.LogIn Prisma.."
  exit 1
fi

###########################################################
### TRANSFORM TASK DEFINITION
###########################################################
# curl has issues with storing the command as variable...
curl -k -X POST \
  https://us-east1.cloud.twistlock.com/us-2-158286731/api/v1/defenders/fargate.json?consoleaddr=us-east1.cloud.twistlock.com\&defenderType=appEmbedded \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary "@$CURRENT_DIR/$ENV/task-definition.json" \
  --output $CURRENT_DIR/$ENV/protected.json

echo "TRANSFORM TASK DEFINITION.1.."

if [[ $? -ne 0 ]] ; then
  echo "Error, exiting deploy script.Transform Task def.."
  exit 1
fi

echo "TRANSFORM TASK DEFINITION.2.."
###########################################################
### REGISTER NEW TASK DEFINITION
###########################################################
TASK_DEFINITION_FILENAME="$CURRENT_DIR/$ENV/protected.json"
# Need to capture the output here
#TASK_DEFINITION_ARN=$(aws ecs register-task-definition \
#  --cli-input-json file://$TASK_DEFINITION_FILENAME \
#  --query 'taskDefinition.taskDefinitionArn' --output text --region us-east-1)

if [ "$2" = "yes" ]; then
  echo "TASK_DEFINITION_ARN.if condition.."
  TASK_DEFINITION_ARN=$(aws ecs register-task-definition \
  			--cli-input-json file://$TASK_DEFINITION_FILENAME \
  			--query 'taskDefinition.taskDefinitionArn' --output text --region us-east-1)
elif [ "$2" = "no" ]; then
  echo "TASK_DEFINITION_ARN.else condition.."
  TASK_DEFINITION_ARN=$(aws ecs describe-task-definition --task-definition $TASK_DEFINITION_NAME \
  				--region us-east-1 --query taskDefinition.taskDefinitionArn --output text)
fi

if [[ -z $TASK_DEFINITION_ARN ]]; then
  echo "Error, exiting deploy script.register new task.."
  exit 1
fi

###########################################################
### CREATE SERVICE IF NOT AVAILABLE
###########################################################
SERVICE_FILENAME="$CURRENT_DIR/$ENV/ocr-service.json"
SERVICE_ARN=$(aws ecs describe-services --cluster uai3046767-cpl-$ENV --services uai3046767-ocr3-service-$ENV --region us-east-1  --query 'services[0].serviceArn' --output text)
echo "SERVICE_ARN : $SERVICE_ARN"
if [[ -z $SERVICE_ARN || $SERVICE_ARN == 'None' ]]; then
	SERVICE_COMMAND="aws ecs create-service --cli-input-json file://$SERVICE_FILENAME --region us-east-1"
	echo "Running SERVICE_COMMAND: $SERVICE_COMMAND"
	if ! $SERVICE_COMMAND; then
		echo "Error, exiting deploy script..."
		exit 1
	fi
fi

###########################################################
### DEPLOY NEW TASK DEFINITION TO ECS/FARGATE
###########################################################
CLUSTER="uai3046767-cpl-$ENV"
SERVICE_NAME="uai3046767-ocr3-service-$ENV"
DEPLOY_COMMAND="aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE_NAME \
  --network-configuration awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUPS],assignPublicIp=DISABLED}
  --task-definition $TASK_DEFINITION_ARN \
  --force-new-deployment \
  --region us-east-1"
echo "Running DEPLOY_COMMAND: $DEPLOY_COMMAND"

if ! $DEPLOY_COMMAND; then
  echo "Error, exiting deploy script..."
  exit 1
fi