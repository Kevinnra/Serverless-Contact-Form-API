# Contact Form API - Serverless Infrastructure

![Status: Under Development](https://img.shields.io/badge/Status-Under%20Development-yellow?style=flat-square)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20DynamoDB%20%7C%20SES-FF9900?style=flat-square&logo=amazon-aws)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)

Production-ready serverless API built with AWS SAM.

## Architecture

- **AWS Lambda**: Contact form handler (Python 3.13)
- **API Gateway**: REST API endpoint 
- **DynamoDB**: Submission storage
- **SES**: Email notifications
- **CloudWatch**: Monitoring and alarms
- **SNS**: Alert notifications
- **GitHub Actions**: CI/CD auto-deploy on push to main

## 🚀 Features

- ✉️ Receives form submissions from [kevinnramirez.com](https://kevinnramirez.com) portfolio website
- ✔️ Validates and sanitizes input data
- 🗄️ Stores submissions in DynamoDB
- 📧 Sends admin email notifications via SES
- ⚡ Returns proper success/error responses
- 🌐 Handles CORS for your domain
- 📊 Includes monitoring and alerts
- 🚦 Rate limiting to prevent abuse (5 req/s, burst 10)
- 🤖 Honeypot spam detection
- 🔄 Automated deployments via GitHub Actions

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

## Testing

### Test with Python Script

```bash
# Setup config file with your API URL
cp config.json.example config.json
# Edit config.json and add your API Gateway URL

# Run integration tests against deployed API
python3 serverless-api/tests/test_contact_form.py
```

### Run Unit Tests
```bash
# Tests Lambda function logic directly (no AWS needed)
cd serverless-api
pip install pytest
pytest tests/test_lambda.py -v
```

### Test with curl-n 
```bash
# Get your API endpoint from stack outputs
aws cloudformation describe-stacks \
  --stack-name contact-form-api-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text

# Test with curl
curl -X POST https://YOUR-API-ID.execute-api.REGION.amazonaws.com/prod/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","message":"Testing contact form"}'

# Expected response:
# {"message": "Thank you for your message! I will get back to you soon.", "success": true}
```

### Test Rate Limiting
```bash
# Send 20 parallel requests - expect ~10 to be throttled
for i in {1..20}; do
  curl -s -o /dev/null -w "Request $i: %{http_code}\n" -X POST YOUR-API-ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{"name":"Test","email":"test@example.com","message":"Rate limit test"}' &
done
wait
```

### Test Honeypot (Bot Detection)
```bash
# Honeypot field filled = bot detected, silently discarded
curl -X POST YOUR-API-ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"name":"Bot","email":"bot@spam.com","message":"spam","honeypot":"im a bot"}'

# Returns 200 to fool the bot, but nothing is stored or emailed
```

### Test XSS / HTML Injection
```bash
curl -X POST YOUR-API-ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"name":"<script>alert(\"xss\")</script>","email":"xss@test.com","message":"<img src=x onerror=alert(1)> Hello"}'

# HTML tags are stripped, special characters escaped before storing
```

### View Logs
```bash
# Tail logs in real-time
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --tail

# View recent logs
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --start-time '10min ago'

# Filter for errors
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --filter 'ERROR'
```

## Commands
```bash
# Build
sam build

# Deploy
sam deploy

# Test deployed API
curl -X POST $(aws cloudformation describe-stacks --stack-name contact-form-api-prod --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text) \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Test message"}'

# View logs (real-time)
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --tail

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