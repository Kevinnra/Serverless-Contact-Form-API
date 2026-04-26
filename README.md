# Serverless Contact Form API

> A production-ready REST API that processes contact form submissions from [kevinnramirez.com](https://kevinnramirez.com). Built entirely on AWS serverless services — no server to manage, no idle cost, auto-deploys on every push to main.

[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/lambda/)
[![API Gateway](https://img.shields.io/badge/AWS-API%20Gateway-FF9900?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/api-gateway/)
[![DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-FF9900?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/dynamodb/)
[![SES](https://img.shields.io/badge/AWS-SES-FF9900?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/ses/)
[![CloudWatch](https://img.shields.io/badge/AWS-CloudWatch-FF9900?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/cloudwatch/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![SAM](https://img.shields.io/badge/AWS-SAM-232F3E?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/serverless/sam/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)

**[Live Demo](https://kevinnramirez.com/#contact)** · **[Portfolio Page](https://kevinnramirez.com)** · **[LinkedIn](https://www.linkedin.com/in/kevinnramirez/)**

---

## Architecture

![Architecture Diagram](docs/images/contact-form-v2.jpg)

Form submissions travel from the portfolio frontend to API Gateway, which rate-limits and routes the request to a Lambda function. The function validates input, strips HTML, checks for bots via a honeypot field, writes to DynamoDB, and sends an email through SES. CloudWatch captures all logs and triggers SNS alerts on error thresholds. Every resource — Lambda, API Gateway, DynamoDB, SES permissions, CloudWatch alarms, SNS topic — is defined in a single SAM template and deployed automatically via GitHub Actions.

The design is intentionally event-driven: no server is running between requests. Cost stays effectively at $0/month within AWS Free Tier for portfolio-level traffic.

---

## Tech Stack

| Service | Role in this project |
|---|---|
| AWS Lambda (Python 3.13) | Executes request handling: validation, sanitization, storage, email dispatch |
| Amazon API Gateway | REST endpoint — enforces rate limiting (5 req/s, burst 10) and CORS |
| Amazon DynamoDB | Stores every validated submission (on-demand capacity) |
| Amazon SES | Sends email notification on each successful submission |
| Amazon CloudWatch | Logs every invocation; alarms trigger on error spikes |
| Amazon SNS | Delivers alert emails when CloudWatch alarms fire |
| AWS SAM + CloudFormation | Defines and provisions all infrastructure as code |
| GitHub Actions | Runs `sam build` and `sam deploy` on every push to `main` |

---

## Features

- **Deployed** a REST API across 6 AWS services from a single SAM template — one command provisions everything
- **Implemented** multi-layer input security: field validation, HTML tag stripping, email format check, and honeypot bot detection
- **Configured** API Gateway throttling at 5 req/s (burst 10) to prevent abuse on a public endpoint
- **Stored** every submission in DynamoDB with UUID partition key, ISO timestamp, sanitized content, and source IP
- **Automated** deployments via GitHub Actions — credentials in GitHub Secrets, config persisted in `samconfig.toml`, zero manual steps after initial setup
- **Set up** CloudWatch alarms that publish to SNS on Lambda error threshold breaches

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

> `samconfig.toml` is generated locally by `sam deploy --guided` and excluded from version control.

</details>

---

## How to Run Locally

**Prerequisites**
- Python 3.13
- AWS CLI configured (`aws configure`)
- AWS SAM CLI (`pip install aws-sam-cli`)
- Two SES-verified email addresses (sender + recipient)

**1. Clone and install**
```bash
git clone https://github.com/Kevinnra/Serverless-Contact-Form-API.git
cd Serverless-Contact-Form-API
```

**2. First deploy (guided — saves config to samconfig.toml)**
```bash
cd serverless-api
sam build
sam deploy --guided
# Prompts: stack name, region, SenderEmail, RecipientEmail, Environment
# Answer Y to save config — subsequent deploys use samconfig.toml automatically
```

**3. Run unit tests (no AWS needed)**
```bash
pip install pytest
pytest tests/test_lambda.py -v
```

**Expected output after deploy:**
```
CloudFormation outputs:
Key                 ApiEndpoint
Value               https://XXXXXX.execute-api.ap-northeast-1.amazonaws.com/prod/contact
```

**4. Test the live endpoint**
```bash
# Happy path — should return 200 with success message
curl -X POST https://YOUR-ENDPOINT/prod/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Hello"}'

# Expected
{"success": true, "message": "Thank you for your message! I will get back to you soon."}
```

**5. Tail live logs**
```bash
# Real-time log stream from Lambda
sam logs -n ContactFormFunction --stack-name contact-form-api-prod --tail
```

---

## Key Decisions

- **Chose AWS SAM over raw CloudFormation** — SAM shorthand cuts the template size significantly for serverless resources; it still compiles to CloudFormation so nothing is abstracted away at deploy time
- **Chose DynamoDB on-demand over provisioned capacity** — traffic is unpredictable and low-volume; paying per request avoids over-provisioning and keeps cost at $0 for portfolio-level use
- **Chose honeypot detection over CAPTCHA** — CAPTCHA adds UX friction; a hidden form field catches most bots silently without affecting real users
- **Chose to keep dependencies minimal** — the Lambda package uses Python stdlib (`re`, `html`, `uuid`, `json`) for sanitization rather than adding external libraries, keeping cold start time low
- **Chose samconfig.toml for CI/CD** — persisting deploy parameters in config means the GitHub Actions workflow runs `sam deploy` without flags, reducing drift between local and CI deployments

---

## Challenges and Solutions

- **Problem:** Lambda function was timing out on the first invocation after a period of inactivity (cold start). Discovered that importing `boto3` at the module level was adding ~400ms. → **Solution:** Confirmed boto3 is always pre-loaded in the Lambda execution environment — no need to import it from a dependency layer. Restructured the handler to keep imports clean and accept cold starts as expected behavior for this traffic pattern.

- **Problem:** SES email sending failed with `MessageRejected` during testing. The error was not obvious from the Lambda logs. → **Solution:** SES sandbox mode only allows sending to verified addresses. Verified both the sender and recipient addresses in the SES console and confirmed the Lambda IAM role had `ses:SendEmail` permission scoped to the verified identity ARN — not `*`.

- **Problem:** GitHub Actions deploy was failing because `sam deploy` was prompting for confirmation interactively in CI. → **Solution:** Added `--no-confirm-changeset --no-fail-on-empty-changeset` flags to the deploy step. These flags make the command non-interactive without disabling safety checks.

- **Problem:** API Gateway was returning `502 Bad Gateway` instead of the Lambda error response during validation failures. → **Solution:** Lambda must always return a properly structured response object (`statusCode`, `headers`, `body`) — even for errors. Wrapping the entire handler in a try/except that returns a `500` response fixed the gateway error.

---

## Lessons Learned

- **SAM templates make IaC accessible, but understanding the underlying CloudFormation matters** — when something failed during deploy, the error was in the CloudFormation stack, not in SAM. Knowing how to read CloudFormation events in the console was necessary to diagnose it.
- **IAM least-privilege is harder in practice than in theory** — the first working version used overly broad permissions. Tightening the Lambda execution role to specific resource ARNs (specific DynamoDB table, specific SES identity) required going back and forth with CloudWatch logs to find what was actually being called.
- **CloudWatch logs are not optional** — without structured logging in the Lambda handler, diagnosing the SES issue would have been much slower. Adding explicit `print()` statements at each stage (receive, validate, sanitize, store, email) made the execution flow visible immediately.
- **The CI/CD pipeline pays off fast** — after the first manual deploy, every subsequent change was a `git push`. That feedback loop accelerated the iteration cycle significantly compared to running `sam deploy` manually each time.
- **Serverless does not mean zero operations** — cold starts, SES sandbox restrictions, IAM scope, and API Gateway response formatting all required deliberate configuration. "Managed" services still need to be understood.

---

## Links

**Live:** [kevinnramirez.com/#contact](https://kevinnramirez.com/#contact)
**Portfolio:** [kevinnramirez.com](https://kevinnramirez.com)
**LinkedIn:** [linkedin.com/in/kevinnramirez](https://www.linkedin.com/in/kevinnramirez/)

---
*Built with ☁️ by [Kevinn Ramirez](https://kevinnramirez.com) | Deployed on AWS*