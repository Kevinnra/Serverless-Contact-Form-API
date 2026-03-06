# Contact Form API - Serverless Infrastructure

![Status: Under Development](https://img.shields.io/badge/Status-Under%20Development-yellow?style=flat-square)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20DynamoDB%20%7C%20SES-FF9900?style=flat-square&logo=amazon-aws)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)

Production-ready serverless API built with AWS SAM.

## Architecture

- **AWS Lambda**: Contact form handler (Python 3.12)
- **API Gateway**: REST API endpoint
- **DynamoDB**: Submission storage
- **SES**: Email notifications
- **CloudWatch**: Monitoring and alarms
- **SNS**: Alert notifications

## 🚀 Features

- ✉️ Receives form submissions from [kevinnramirez.com](https://kevinnramirez.com) portfolio website
- ✔️ Validates and sanitizes input data
- 🗄️ Stores submissions in DynamoDB
- 📧 Sends admin email notifications via SES
- ⚡ Returns proper success/error responses
- 🌐 Handles CORS for your domain
- 📊 Includes monitoring and alerts

## Prerequisites

- AWS CLI configured
- AWS SAM CLI installed
- Verified SES email addresses

## Deployment

### Deploy to Production
```bash
sam build
sam deploy --guided

# Follow prompts:
# Stack name: contact-form-api-prod
# AWS Region: ap-northeast-1
# Parameter SenderEmail: your-verified-email@example.com
# Parameter RecipientEmail: your-email@example.com
# Parameter Environment: prod
# Confirm changes: Y
# Allow SAM CLI IAM role creation: Y
# Save arguments to config: Y
```

### Local Testing
```bash
# Test Lambda function locally
sam local invoke ContactFormFunction -e events/test-event.json

# Start API Gateway locally
sam local start-api

# Test with curl
curl -X POST http://localhost:3000/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Local test"}'
```

## Commands
```bash
# Build
sam build

# Deploy
sam deploy

# View logs
sam logs -n ContactFormFunction --tail

# Delete stack
sam delete
```

## Outputs

After deployment, SAM outputs:
- API Endpoint URL
- Lambda Function ARN
- DynamoDB Table Name
- SNS Topic ARN

Use API Endpoint in your frontend!

## 📝 Status

> **⚠️ Under Development** - This project is actively being worked on. Features and API may change.

---

*Built with ☁️ by [Kevinn Ramirez](https://kevinnramirez.com)*