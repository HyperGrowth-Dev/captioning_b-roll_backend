#!/bin/bash

# Create a temporary directory for the deployment package
mkdir -p deploy

# Copy the Lambda function
cp index.js deploy/

# Install dependencies
cd deploy
npm init -y
npm install @remotion/bundler @remotion/renderer @sparticuz/chromium puppeteer-core

# Create the deployment package
zip -r ../deployment.zip .

# Clean up
cd ..
rm -rf deploy

# Deploy to AWS Lambda
aws lambda update-function-code \
    --function-name caption-remotion \
    --zip-file fileb://deployment.zip

# Clean up deployment package
rm deployment.zip