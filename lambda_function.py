import json
import boto3
import os
from datetime import datetime
import logging
import re
import html

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
ses_client = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'))

# Environment variables - REQUIRED, will fail if not set
try:
    TABLE_NAME = os.environ['TABLE_NAME']
    SENDER_EMAIL = os.environ['SENDER_EMAIL']
    RECIPIENT_EMAIL = os.environ['RECIPIENT_EMAIL']
except KeyError as e:
    logger.error(f"Missing required environment variable: {e}")
    raise

def sanitize_input(text, max_length=1000):
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    
    text = re.sub(r'<[^>]*>', '', text)
    text = html.escape(text)
    text = text.strip()
    text = text[:max_length]
    
    return text

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def lambda_handler(event, context):
    """Main handler function"""
    
    logger.info({
        'event': 'request_received',
        'request_id': context.request_id
    })
    
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Check honeypot
        honeypot = body.get('honeypot', '')
        if honeypot:
            logger.warning({
                'event': 'spam_detected',
                'reason': 'honeypot_filled'
            })
            return create_response(200, {
                'message': 'Thank you for your message!',
                'success': True
            })
        
        # Extract and sanitize
        name = sanitize_input(body.get('name', ''), max_length=100)
        email = sanitize_input(body.get('email', ''), max_length=100)
        message = sanitize_input(body.get('message', ''), max_length=1000)
        
        # Validate
        if not name or not email or not message:
            return create_response(400, {
                'error': 'All fields are required'
            })
        
        if not validate_email(email):
            return create_response(400, {
                'error': 'Invalid email address'
            })
        
        if len(message) < 10:
            return create_response(400, {
                'error': 'Message must be at least 10 characters'
            })
        
        # Store in DynamoDB
        timestamp = int(datetime.now().timestamp())
        table = dynamodb.Table(TABLE_NAME)
        
        table.put_item(
            Item={
                'email': email,
                'timestamp': timestamp,
                'name': name,
                'message': message,
                'status': 'new',
                'submittedAt': datetime.now().isoformat()
            }
        )
        
        logger.info({
            'event': 'submission_stored',
            'email': email,
            'timestamp': timestamp
        })
        
        # Send email
        email_sent = send_email_notification(name, email, message)
        
        return create_response(200, {
            'message': 'Thank you for your message! I will get back to you soon.',
            'success': True
        })
        
    except json.JSONDecodeError:
        logger.error({'event': 'json_decode_error'})
        return create_response(400, {'error': 'Invalid JSON format'})
    
    except Exception as e:
        logger.error({
            'event': 'unexpected_error',
            'error': str(e)
        })
        return create_response(500, {
            'error': 'Internal server error'
        })

def send_email_notification(name, email, message):
    """Send email via SES"""
    try:
        subject = f"New Contact Form Submission from {name}"
        
        body_text = f"""
New contact form submission:

Name: {name}
Email: {email}

Message:
{message}

---
Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECIPIENT_EMAIL]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Text': {'Data': body_text, 'Charset': 'UTF-8'}}
            }
        )
        
        logger.info({'event': 'email_sent', 'message_id': response['MessageId']})
        return True
        
    except Exception as e:
        logger.error({'event': 'email_failed', 'error': str(e)})
        return False

def create_response(status_code, body):
    """Create HTTP response with CORS"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body)
    }