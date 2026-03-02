import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
ses_client = boto3.client('ses', region_name='ap-northeast-1')

# Environment variables for configuration
TABLE_NAME = os.environ.get('TABLE_NAME', 'ContactFormSubmissions')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'your-verified-email@example.com')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', 'your-email@example.com')

def lambda_handler(event, context):
    """
    Main Lambda handler function
    Processes contact form submissions
    """
    
    # Log the incoming event for debugging
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the request body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Extract form data
        email = body.get('email', '').strip()
        name = body.get('name', '').strip()
        message = body.get('message', '').strip()
        
        # Validate required fields
        if not email or not name or not message:
            return create_response(400, {
                'error': 'Missing required fields',
                'required': ['email', 'name', 'message']
            })
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return create_response(400, {
                'error': 'Invalid email format'
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
        
        print(f"Stored submission from {email} at {timestamp}")
        
        # Send email notification
        send_email_notification(name, email, message)
        
        # Return success response
        return create_response(200, {
            'message': 'Thank you for your message! I will get back to you soon.',
            'success': True
        })
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON in request body")
        return create_response(400, {
            'error': 'Invalid JSON format'
        })
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': 'An error occurred while processing your submission'
        })

def send_email_notification(name, email, message):
    """
    Send email notification via SES
    """
    try:
        subject = f"New Contact Form Submission from {name}"
        
        body_text = f"""
        New contact form submission received!
        
        Name: {name}
        Email: {email}
        
        Message:
        {message}
        
        ---
        Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                'ToAddresses': [RECIPIENT_EMAIL]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        print(f"Email sent successfully: {response['MessageId']}")
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        # Don't fail the whole request if email fails
        pass

def create_response(status_code, body):
    """
    Create HTTP response with CORS headers
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # We'll restrict this later
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body)
    }