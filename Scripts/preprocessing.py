import pandas as pd
import boto3
from sklearn.model_selection import train_test_split

# S3 paths
s3_input_path = "s3://creditcard-pipeline-bucket/train/creditcard.csv"
s3_output_path = "s3://creditcard-pipeline-bucket/processed/"

# Load CSV from S3
df = pd.read_csv(s3_input_path)

# Handle missing values
df.fillna(0, inplace=True)

# Split into features and target
X = df.drop('Class', axis=1)
y = df['Class']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Combine features and target
train = pd.concat([X_train, y_train], axis=1)
test = pd.concat([X_test, y_test], axis=1)

# Save processed data locally in /tmp (Notebook instance temp storage)
train.to_csv("/tmp/train.csv", index=False)
test.to_csv("/tmp/test.csv", index=False)

# Upload processed data back to S3
s3 = boto3.client('s3')
s3.upload_file("/tmp/train.csv", "creditcard-pipeline-bucket", "processed/train.csv")
s3.upload_file("/tmp/test.csv", "creditcard-pipeline-bucket", "processed/test.csv")

print("Data preprocessing complete. Processed files uploaded to S3.")
