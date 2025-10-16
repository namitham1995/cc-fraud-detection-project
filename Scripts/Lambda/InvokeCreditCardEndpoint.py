import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

runtime = boto3.client('sagemaker-runtime')
sns = boto3.client('sns')

ENDPOINT_NAME = 'creditcard-endpoint'
SNS_TOPIC_ARN = 'arn:aws:sns:ap-south-1:546736804387:FraudAlertsTopic'

def lambda_handler(event, context):
    logger.info("🔸 RAW EVENT: %s", json.dumps(event))

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS" or event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "content-type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({"message": "CORS OK"})
        }

    # Handle both test events and real API events
    if "body" in event:
        body = json.loads(event["body"])
    else:
        body = event

    logger.info("🟢 PARSED BODY: %s", body)

    features = body["features"]
    payload = [features]

    # Call SageMaker
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload)
    )

    prediction = json.loads(response['Body'].read().decode())[0]
    logger.info("📊 MODEL PREDICTION: %s", prediction)

    # If fraud, send email via SNS
    if prediction == 1:
        message = f"🚨 Fraudulent transaction detected!\n\nFeatures: {features}"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="🚨 Fraud Alert",
            Message=message
        )
        logger.info("📩 SNS Fraud Alert Sent")

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Methods": "POST,OPTIONS"
        },
        "body": json.dumps({"prediction": prediction})
    }
