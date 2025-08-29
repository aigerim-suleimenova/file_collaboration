import boto3
import os
from botocore.exceptions import ClientError


class S3Manager:
    def __init__(self, bucket_name, region='us-east-1'):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=region)
        self.s3_resource = boto3.resource('s3', region_name=region)

    def create_bucket(self):
        """Create S3 bucket"""
        try:
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' created successfully!")
            return True
        except ClientError as e:
            print(f"❌ Error creating bucket: {e}")
            return False

    def upload_file(self, local_file, s3_key):
        """Upload a single file to S3"""
        try:
            self.s3_client.upload_file(local_file, self.bucket_name, s3_key)
            print(
                f"✅ Uploaded {local_file} to s3://{self.bucket_name}/{s3_key}")
            return True
        except ClientError as e:
            print(f"❌ Error uploading file: {e}")
            return False

    def upload_directory(self, local_dir, s3_prefix=""):
        """Upload entire directory to S3"""
        try:
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    s3_key = os.path.join(s3_prefix, local_path)
                    self.upload_file(local_path, s3_key)
            print(f"✅ Directory {local_dir} uploaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error uploading directory: {e}")
            return False

    def download_file(self, s3_key, local_file):
        """Download a file from S3"""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_file)
            print(
                f"✅ Downloaded s3://{self.bucket_name}/{s3_key} to {local_file}")
            return True
        except ClientError as e:
            print(f"❌ Error downloading file: {e}")
            return False

    def list_files(self, prefix=""):
        """List files in S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' in response:
                print(f"📁 Files in s3://{self.bucket_name}/{prefix}:")
                for obj in response['Contents']:
                    print(f"  - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print(f"📁 No files found in s3://{self.bucket_name}/{prefix}")
        except ClientError as e:
            print(f"❌ Error listing files: {e}")

    def delete_file(self, s3_key):
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            print(f"✅ Deleted s3://{self.bucket_name}/{s3_key}")
            return True
        except ClientError as e:
            print(f"❌ Error deleting file: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize S3 manager
    bucket_name = "your-project-bucket-2024"
    s3_manager = S3Manager(bucket_name)

    # Create bucket
    s3_manager.create_bucket()

    # Upload your project files
    print("\n📤 Uploading project files...")
    s3_manager.upload_directory("./backend", "backend")
    s3_manager.upload_directory("./frontend", "frontend")

    # List all files
    print("\n📋 Listing all files:")
    s3_manager.list_files()

    # Download example
    print("\n📥 Downloading example file:")
    s3_manager.download_file("backend/requirements.txt",
                             "./downloaded-requirements.txt")
