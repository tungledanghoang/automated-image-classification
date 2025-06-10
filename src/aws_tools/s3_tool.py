import os
import boto3
from typing import List


class S3Manager:
    """
    Simple class providing methods for getting files from S3 and clearing files from local storage
    """

    def __init__(self, bucket_name: str):
        self.s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_ID'],
                               aws_secret_access_key=os.environ['AWS_ACCESS_KEY'],
                               region_name=os.environ['AWS_REGION'])
        response = [bucket['Name'] for bucket in self.s3.list_buckets()['Buckets']]
        if bucket_name not in response:
            raise ValueError(f"Bucket {bucket_name} does not exist")
        self.bucket_name = bucket_name
        if not os.path.exists("tmp"):
            os.mkdir("tmp")

    def get_file(self, file_name: str) -> str:
        """
        Get files from S3 bucket and save them to a tmp folder

        Args:
            file_name (str): file name in S3 bucket

        Returns:
            Path to saved file
        """
        self.s3.download_file(self.bucket_name, file_name, f'tmp\\{file_name}')
        return f'tmp\\{file_name}'

    @classmethod
    def clear_files(cls, file_paths: List[str]):
        """
        Delete files saved from S3 bucket from local storage

        Args:
            list of paths to saved files to be deleted
        """
        for path in file_paths:
            os.remove(path)
