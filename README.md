# Automated Image Classification
This is the source code for an automated image classification service. The service is designed to poll messages containing information of images on S3 buckets from an AWS SQS queue, get those images, classify them and send the results to another SQS queue

## Running the service
An .env file needs to be created in root directory with the following fields:

```
AWS_ACCESS_ID: AWS access id used along with the AWS secret access key
AWS_ACCESS_KEY: AWS secret access key
AWS_REGION: AWS region to be used for both SQS and S3
SQS_QUEUE_NAME: Queue name of SQS queue for polling image classification requests
SQS_RESULT_QUEUE_NAME: Queue name of SQS queue for sending classification results
MODEL_NAME: Image classification model name. Currently support resnet18, resnet34 and resnet50
```
### After the .env file is created, the service can be started by one of two ways:
#### Normal installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the necessary library/framework using the requirements.txt file
```bash
pip install -r requirements.txt
python3 main.py
```
#### Docker installation
```bash
docker build -t automated_image_clasification .
docker run automated_image_clasification:latest
```

## Running test
Testing can be done by running the follow command at root folder
```bash
pytest
```
Please make sure the requirements has been installed with pip

In the case of running the service on Docker, the service has been setup to automatically run pytest and will fail to build if all tests are not passed

## Logging
The service activities are logged in real-time and saved into a log.txt file located at root. The file is created automatically on start

## Stopping the service
If running on console command, the service can be stopped by pressing Ctrl + C

If running on Docker, the service has been set up to gracefully exit upon stopping the container