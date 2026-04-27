# Serverless Contact Form API

> REST API that processes contact form submissions from [kevinnramirez.com](https://kevinnramirez.com) — built entirely on AWS serverless services, defined as Infrastructure as Code, and deployed automatically on every push to main.

[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/lambda/)
[![API Gateway](https://img.shields.io/badge/AWS-API%20Gateway-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/api-gateway/)
[![DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-FF9900?style=flat-square&logo=amazondynamodb&logoColor=white)](https://aws.amazon.com/dynamodb/)
[![SES](https://img.shields.io/badge/AWS-SES-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/ses/)
[![CloudWatch](https://img.shields.io/badge/AWS-CloudWatch-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/cloudwatch/)
[![SNS](https://img.shields.io/badge/AWS-SNS-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/sns/)
[![SAM](https://img.shields.io/badge/AWS-SAM-232F3E?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/serverless/sam/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)

**[Live Demo](https://kevinnramirez.com/#contact)** · **[Portfolio Page](https://kevinnramirez.com/projects/project.html?id=serverless-api)** · **[LinkedIn](https://www.linkedin.com/in/kevinnramirez/)**

---

## Architecture

![Architecture Diagram](docs/images/contact-form-v2.jpg)

Form submissions travel from the portfolio frontend to API Gateway, which enforces rate limiting before passing the request to Lambda. The function validates and sanitizes all input, silently discards bot submissions via a honeypot field, writes the record to DynamoDB, and dispatches a notification email through SES. CloudWatch captures every invocation log and fires SNS alerts when errors cross a defined threshold. Every resource is defined in a single SAM template and provisioned through CloudFormation — no manual infrastructure setup.

---

## Tech Stack

| Service | Purpose |
|---|---|
| AWS Lambda (Python 3.13) | Validates input, sanitizes content, writes to DynamoDB, sends email via SES |
| Amazon API Gateway | Public REST endpoint — rate limiting, CORS, TLS termination |
| Amazon DynamoDB | Stores every validated submission with on-demand billing |
| Amazon SES | Sends email notification on each successful submission |
| Amazon CloudWatch | Captures Lambda invocation logs; triggers alarms on error spikes |
| Amazon SNS | Delivers alert emails when CloudWatch alarms fire |
| AWS SAM + CloudFormation | Defines and provisions all infrastructure as code |
| GitHub Actions | Runs `sam build` + `sam deploy` on every push to `main` |

---

## Features

- **Deployed** a full serverless API stack across 6 AWS services from a single SAM template
- **Implemented** multi-layer input security: field validation, HTML sanitization, email format check, and honeypot bot detection
- **Configured** API Gateway rate limiting at 5 req/s (burst 10) with CORS restricted to the portfolio domain
- **Stored** every validated submission in DynamoDB with UUID partition key, ISO timestamp, sanitized content, and source IP
- **Automated** end-to-end deployments via GitHub Actions — credentials in GitHub Secrets, config persisted in `samconfig.toml`, zero manual steps after initial setup
- **Set up** CloudWatch alarms that publish to SNS on Lambda error threshold breaches
- **Wired** the live endpoint into the portfolio contact form with loading states and user-facing error handling

---

## Project Structure

<details>
<summary>View full structure</summary>

```
.
├── .github/
│   └── workflows/
│       └── deploy-serverless-api.yaml  # CI/CD — triggers sam build + deploy on push to main
├── docs/
│   ├── images/
│   │   └── contact-form-v2.jpg         # Architecture diagram
│   └── DEPLOYMENT.md                   # Step-by-step deployment guide
├── serverless-api/
│   ├── events/
│   │   └── test-event.json             # Sample event payload for local Lambda testing
│   ├── src/
│   │   ├── __init__.py
│   │   └── lambda_function.py          # Lambda handler — validation, sanitization, DynamoDB, SES
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_lambda.py              # Unit tests — no AWS required
│   ├── conftest.py                     # Pytest fixtures and shared test config
│   ├── requirements.txt                # Python dependencies
│   ├── samconfig.toml                  # SAM deploy config — generated on first guided deploy
│   └── template.yaml                   # SAM template — defines all AWS resources
├── .gitignore
├── README.md
├── config.json.example                 # Config template — copy to config.json and populate
└── serverless-deploy-policy.json       # Least-privilege IAM policy for the deploy user
```

</details>

---

## How to Run Locally

**Prerequisites**
- Python 3.13
- AWS CLI configured (`aws configure`)
- AWS SAM CLI (`pip install aws-sam-cli`)
- Two SES-verified email addresses (sender + recipient)

**1. Clone the repo**
```bash
git clone https://github.com/Kevinnra/Serverless-Contact-Form-API.git
cd Serverless-Contact-Form-API/serverless-api
```

**2. First deploy — guided mode saves config to `samconfig.toml`**
```bash
sam build
sam deploy --guided
# Prompts: stack name, region, SenderEmail, RecipientEmail, Environment
# Save to samconfig.toml when prompted — subsequent deploys use it automatically
```

**Expected output after deploy:**
```
CloudFormation outputs:
Key                 ApiEndpoint
Value               https://XXXXXX.execute-api.ap-northeast-1.amazonaws.com/prod/contact
```

**3. Run unit tests (no AWS required)**
```bash
pip install pytest
pytest tests/test_lambda.py -v
```

**4. Test the live endpoint**
```bash
# Valid submission
curl -X POST https://YOUR-ENDPOINT/prod/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Hello"}'

# Expected response
{"success": true, "message": "Thank you for your message! I will get back to you soon."}
```

**5. Tail Lambda logs in real time**
```bash
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --tail
```

---

## Key Decisions

- **Chose AWS SAM over raw CloudFormation** — SAM shorthand for Lambda and API Gateway is far more concise; it compiles to CloudFormation at deploy time so nothing is hidden from the actual provisioning process
- **Chose DynamoDB on-demand over provisioned capacity** — traffic is unpredictable and low-volume; on-demand billing means $0 at zero requests with no capacity to pre-configure or monitor
- **Chose honeypot detection over CAPTCHA** — a hidden form field silently discards bots without adding friction for real users or introducing a third-party dependency
- **Chose Python stdlib for sanitization** — `re` and `html` from the standard library handle tag stripping and character escaping without adding external packages, keeping the deployment package small and cold starts fast
- **Chose `samconfig.toml` to persist deploy parameters** — both local deploys and the CI pipeline run `sam deploy` with no flags, eliminating drift between environments

---

## Challenges and Solutions

- **Problem:** SES returned `MessageRejected` but Lambda logs showed no useful detail about the cause. → **Solution:** SES sandbox mode only allows sending to individually verified addresses. Verified both sender and recipient in the SES console, then confirmed the Lambda IAM role was scoped to `ses:SendEmail` on the specific verified sender identity ARN — not a wildcard resource.

- **Problem:** API Gateway returned `502 Bad Gateway` when the Lambda function threw an unhandled exception, making the actual error invisible to the frontend. → **Solution:** API Gateway requires Lambda to always return a response object with `statusCode`, `headers`, and `body`. Wrapped the entire handler in `try/except` so every code path returns a valid structured response.

- **Problem:** `sam deploy` hung indefinitely in the GitHub Actions pipeline with no output. → **Solution:** SAM was waiting for interactive changeset confirmation — the same prompt that appears locally. Added `--no-confirm-changeset` and `--no-fail-on-empty-changeset` flags to make the command non-interactive without disabling changeset safety.

---

## Cost Breakdown

| Service | Est. Monthly Cost | Note |
|---|---|---|
| AWS Lambda | $0.00 | Free Tier covers 1M requests/month — portfolio traffic is well within this |
| Amazon API Gateway | $0.00 | Free Tier covers 1M REST API calls/month for the first 12 months |
| Amazon DynamoDB | $0.00 | On-demand billing — Free Tier covers 25 WCU/RCU; portfolio write volume is negligible |
| Amazon SES | $0.00 | Free Tier covers 3,000 messages/month sent from Lambda |
| Amazon CloudWatch | $0.00 | Free Tier covers 5GB log ingestion/month and 10 custom alarms |
| Amazon SNS | $0.00 | Free Tier covers 1,000 email notifications/month |
| **Total** | **$0.00/mo** | |

Dev/learning setup — production workloads would cost more.

---

## Lessons Learned

- **SAM errors surface in CloudFormation, not in the SAM CLI output** — when a deploy failed, the useful error message was in the CloudFormation stack events in the AWS console; knowing where to look saved significant time
- **IAM least-privilege requires iteration** — the first working version used permissions that were too broad; tightening them to specific resource ARNs meant reading CloudWatch logs carefully to confirm exactly what each service call needed at runtime
- **Structured logging is not optional** — adding explicit log statements at each stage of the handler (receive, validate, store, email) made it possible to isolate failures immediately; without them, diagnosing the SES sandbox issue would have taken much longer
- **CI/CD pays off fast** — after the first manual deploy, every subsequent change was a `git push`; the feedback loop made iteration significantly faster than running `sam deploy` by hand each time
- **Serverless does not mean zero configuration** — cold starts, SES sandbox restrictions, IAM scope, and the Lambda-API Gateway response contract all required deliberate decisions; managed services still need to be understood

---

## Links

- **Live:** [kevinnramirez.com/#contact](https://kevinnramirez.com/#contact)
- **Portfolio**: [kevinnramirez.com](https://www.kevinnramirez.com/projects/project-v3.html?id=aws-portfolio)
- **LinkedIn**: [linkedin.com/in/kevinnramirez](https://linkedin.com/in/kevinnramirez)


---

**Built with ☁️ by Kevin Ramirez** | Cloud Engineer