# Deployment Guide

## Prerequisites
- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed (`pip install aws-sam-cli`)
- Verified SES email addresses (sender + recipient)
- GitHub repository with Actions enabled

## Step 1: Clone and Configure
```bash
git clone https://github.com/Kevinnra/Serverless-Contact-Form-API.git
cd Serverless-Contact-Form-API
cp config.json.example config.json
# Edit config.json with your API Gateway URL after first deploy
```

## Step 2: Set GitHub Secrets
In your repo → Settings → Secrets → Actions, add:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION (e.g. ap-northeast-1)
```

## Step 3: Deploy
```bash
cd serverless-api
sam build
sam deploy --guided

# Prompts:
# Stack name:          contact-form-api-prod
# AWS Region:          ap-northeast-1
# SenderEmail:         your-verified@email.com
# RecipientEmail:      your-email@email.com
# Environment:         prod
# Confirm changes:     Y
# Allow IAM creation:  Y
# Save to config:      Y
```

After this, every push to `main` deploys automatically.

## Step 4: Connect to Frontend
Copy the `ApiEndpoint` output URL into your frontend's contact form handler.

## Troubleshooting

### SES Sandbox Mode
By default, AWS SES operates in sandbox mode. You can only send to verified email addresses. To move to production:
1. Request production access in SES settings
2. Update `template.yaml` with new email configuration

### Cold Start Delays
Lambda functions may take 500ms+ on first invocation. This is acceptable for portfolio contact forms.

## View Live Logs
```bash
# Real-time tail
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --tail

# Recent logs
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --start-time '10min ago'

# Filter errors only
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --filter 'ERROR'
```
