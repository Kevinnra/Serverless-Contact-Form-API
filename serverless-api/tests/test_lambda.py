import json
import pytest
import boto3
import os
from unittest.mock import MagicMock
from moto import mock_aws

# Set required env vars before importing lambda_function
os.environ['TABLE_NAME'] = 'test-table'
os.environ['SENDER_EMAIL'] = 'sender@example.com' 
os.environ['RECIPIENT_EMAIL'] = 'recipient@example.com'
os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1' 
os.environ['AWS_ACCESS_KEY_ID'] = 'test' 
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test' 

from src import lambda_function

# Mock Lambda context object (replaces real AWS Lambda context)
context = MagicMock()
context.aws_request_id = 'test-request-id'


def create_table():
    """Creates a local mock DynamoDB table matching production schema"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    dynamodb.create_table(
        TableName='test-table',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'},
            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'N'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )


@pytest.fixture 
def aws_setup():
    """
    Pytest fixture: spins up a mocked AWS environment for each test.
    Tests that need DynamoDB use this fixture as a parameter.
    The mock is torn down automatically after each test.
    """
    with mock_aws():
        create_table()
        yield boto3.resource('dynamodb', region_name='ap-northeast-1')


def test_successful_submission(aws_setup):
    """Valid submission should store in DynamoDB and return 200"""
    event = {'body': json.dumps({
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'This is a test message for unit testing'
    })}
    response = lambda_function.lambda_handler(event, context)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['success'] == True


def test_missing_fields():
    """
    No @mock_aws needed - validation fails before hitting DynamoDB.
    Tests that lambda returns 400 when required fields are missing.
    """
    event = {'body': json.dumps({'name': 'Test User'})}
    response = lambda_function.lambda_handler(event, context)
    assert response['statusCode'] == 400
    assert 'error' in json.loads(response['body'])


def test_invalid_email():
    """
    No @mock_aws needed - email validation fails before hitting DynamoDB.
    Tests that lambda returns 400 for invalid email format.
    """
    event = {'body': json.dumps({
        'name': 'Test User',
        'email': 'invalid-email',
        'message': 'Test message'
    })}
    response = lambda_function.lambda_handler(event, context)
    assert response['statusCode'] == 400


def test_honeypot_spam_detection(aws_setup):
    """
    Honeypot field filled = bot detected.
    Should return 200 (to fool the bot) but NOT store anything in DynamoDB.
    """
    event = {'body': json.dumps({
        'name': 'Spammer',
        'email': 'spam@spam.com',
        'message': 'Spam message',
        'honeypot': 'I am a bot'
    })}
    response = lambda_function.lambda_handler(event, context)

    # Returns 200 to fool the bot
    assert response['statusCode'] == 200

    # Verify nothing was stored in DynamoDB
    table = aws_setup.Table('test-table')
    result = table.scan(
        FilterExpression='email = :e',
        ExpressionAttributeValues={':e': 'spam@spam.com'}
    )
    assert result['Count'] == 0


def test_input_sanitization():
    """HTML tags should be stripped, content preserved (XSS prevention)"""
    sanitized = lambda_function.sanitize_input('<script>alert("XSS")</script>')
    assert '<script>' not in sanitized
    assert 'alert' in sanitized


def test_email_validation():
    """Email validator should accept valid and reject invalid formats"""
    assert lambda_function.validate_email('valid@example.com') == True
    assert lambda_function.validate_email('invalid.email') == False
    assert lambda_function.validate_email('@example.com') == False
