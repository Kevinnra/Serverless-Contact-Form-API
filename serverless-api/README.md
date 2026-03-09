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

## Testing

### Test with Python Script 

```bash
python3 [test_contact_form.py](events/test_contact_form.py)
```

Expected output:
```
Testing Contact Form API

✓ Valid submission: 200
  Response: {'message': 'Thank you for your message! I will get back to you soon.', 'success': True}

✓ Invalid email: 400
  Response: {'error': 'Invalid email format', 'success': False}

✓ Empty fields: 400
  Response: {'error': 'All fields are required', 'success': False}

All tests completed!
```

### Test with curl
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