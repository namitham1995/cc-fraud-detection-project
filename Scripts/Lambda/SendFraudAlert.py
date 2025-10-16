import json
import boto3

sns = boto3.client('sns')
topic_arn = "arn:aws:sns:ap-south-1:546736804387:FraudAlertsTopic"  # Replace with your topic ARN

def lambda_handler(event, context):
    # Example: event contains prediction result
    result = json.loads(event["body"])
    prediction = result["prediction"]
    
    if prediction == 1:  # Fraud detected
        message = "🚨 Fraudulent transaction detected!"
        sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="Fraud Alert"
        )
    
    return {"statusCode": 200, "body": json.dumps({"message": "SNS triggered"})}
