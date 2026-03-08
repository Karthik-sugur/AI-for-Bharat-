<# 
LandLedger Backend - AWS Elastic Beanstalk Deployment Script
Run this script from the backend folder
#>

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "LandLedger AWS Elastic Beanstalk Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Configuration
$APP_NAME = "landledger-backend"
$ENV_NAME = "landledger-env"
$REGION = "us-east-1"

# Step 1: Check if AWS CLI is installed
Write-Host "`n[Step 1] Checking AWS CLI..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version
    Write-Host "AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI not found. Please install it from https://aws.amazon.com/cli/" -ForegroundColor Red
    exit 1
}

# Step 2: Check if EB CLI is installed
Write-Host "`n[Step 2] Checking EB CLI..." -ForegroundColor Yellow
try {
    $ebVersion = eb --version
    Write-Host "EB CLI found: $ebVersion" -ForegroundColor Green
} catch {
    Write-Host "EB CLI not found. Installing..." -ForegroundColor Yellow
    pip install awsebcli
}

# Step 3: Configure AWS credentials
Write-Host "`n[Step 3] Configuring AWS credentials..." -ForegroundColor Yellow
Write-Host "Make sure you have run 'aws configure' with your Access Key and Secret Key" -ForegroundColor White

# Step 4: Initialize Elastic Beanstalk
Write-Host "`n[Step 4] Initializing Elastic Beanstalk application..." -ForegroundColor Yellow
eb init $APP_NAME --platform "Python 3.11" --region $REGION

# Step 5: Create environment (if not exists) or deploy
Write-Host "`n[Step 5] Creating/Deploying to environment..." -ForegroundColor Yellow
$envExists = eb list | Select-String $ENV_NAME
if ($envExists) {
    Write-Host "Environment exists. Deploying..." -ForegroundColor Green
    eb deploy $ENV_NAME
} else {
    Write-Host "Creating new environment..." -ForegroundColor Green
    eb create $ENV_NAME --single --instance-type t3.small
}

# Step 6: Set environment variables
Write-Host "`n[Step 6] Setting environment variables..." -ForegroundColor Yellow
Write-Host "IMPORTANT: Set these in AWS Console > Elastic Beanstalk > Configuration > Software" -ForegroundColor White
Write-Host @"

Required Environment Variables:
  AWS_REGION=us-east-1
  DYNAMODB_TABLE_NAME=landledger-cache
  DYNAMODB_LAND_RECORDS_TABLE=landledger-land-records
  S3_BUCKET_NAME=landledger-documents
  BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

Note: AWS credentials are inherited from the EC2 instance role (aws-elasticbeanstalk-ec2-role)
Make sure this role has permissions for: DynamoDB, S3, Bedrock, Polly, Textract

"@ -ForegroundColor Cyan

# Step 7: Open application
Write-Host "`n[Step 7] Opening application..." -ForegroundColor Yellow
eb open

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
