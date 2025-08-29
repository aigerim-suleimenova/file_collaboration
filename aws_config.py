# AWS Configuration
# Replace these with your actual AWS credentials

AWS_ACCESS_KEY_ID = 'your-access-key-here'
AWS_SECRET_ACCESS_KEY = 'your-secret-key-here'
AWS_REGION = 'us-east-1'  # Change to your preferred region

# S3 Bucket Configuration
S3_BUCKET_NAME = 'your-project-bucket-2024'

# Example usage:
# from aws_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
#
# s3_client = boto3.client(
#     's3',
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name=AWS_REGION
# )
