import os
import pytest
from src.aws_tools import S3Manager


@pytest.fixture(scope="module")
def s3(moto_aws_mock):
    _, s3_client = moto_aws_mock
    s3_client.upload_file("tests/images/kitchen.jpg", os.environ['S3_BUCKET_NAME'], "kitchen.jpg")
    s3_client.upload_file("tests/images/living_room.jpg", os.environ['S3_BUCKET_NAME'], "living_room.jpg")
    s3_manager = S3Manager(bucket_name=os.environ['S3_BUCKET_NAME'])
    return s3_manager


def test_s3_get_file(s3, namespace):
    file_paths = s3.get_files(["kitchen.jpg", "living_room.jpg"])
    namespace['file_paths'] = file_paths
    for file_path in file_paths:
        assert os.path.isfile(file_path)


def test_s3_local_file_delete(s3, namespace):
    s3.clear_files(namespace['file_paths'])
    for file_path in namespace['file_paths']:
        assert not os.path.isfile(file_path)
