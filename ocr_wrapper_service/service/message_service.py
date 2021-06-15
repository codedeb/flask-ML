import json

import boto3
import csv
from botocore.config import Config


def process_sqs_messages():
    # sqs_client = boto3.client('sqs', config=Config(proxies={'https': 'cis-americas-pitc-cinciz.proxy.corporate.gtm.ge.com:80'}))
    sqs_client = boto3.client('sqs', region_name='us-east-1')
    queue_urls = sqs_client.list_queues()['QueueUrls']
    print('queue_urls', queue_urls)
    response = sqs_client.receive_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/386826140800/di-sqs-cpl-idm',
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1
    )
    response_list = []
    # response = {'Messages': [{'MessageId': 'd48109f5-80e3-4fe0-997e-a80560045869', 'ReceiptHandle': 'AQEBEyhQx1auDFJcqDsR4t55bFkWz8/ZvT+AxU9a24zVg7xQkCsohv2u64jP7QldsPT/6rRCf/JG/gpiiAUHrjhbg7eWJPAnw7P0hWvkJ9eSAXZLmXlRtt2NW8J4AKLHo4LrufnD3x/8qQGW3fLYD5nlC+Vz5WCFT0lRrb2yIzWSpvxE8xioIXJhTeit1mIi7REly3sxrqRorcc/dgATo24krRaTmUWNg+SANOYowBXHSblIYPVQhrRAJyc5M/rfSgwSaoaKh7hH7fiXj87cmNeO8XTobRpsVAyVBvzLvcESYTIGOHBmNso7zzGqzUnm/eWXvhhKnAx51hsJz1lmyTta9uhoeCSMWWF/0aJEhlki+R+VhIzkh1f2jx0Y/t7BatF8ksXXDD4oRPbN/Mxm7IwkvQ==', 'MD5OfBody': '3c56ad1ac3ee18c92e4a6a4a722d33b7', 'Body': '{"Records":[{"eventVersion":"2.1","eventSource":"aws:s3","awsRegion":"us-east-1","eventTime":"2021-04-30T12:03:29.553Z","eventName":"ObjectCreated:Copy","userIdentity":{"principalId":"AWS:AROAVUEFCPSAFDLTGFDAT:223019194"},"requestParameters":{"sourceIPAddress":"165.156.29.92"},"responseElements":{"x-amz-request-id":"PD40SK36M9ECZDJF","x-amz-id-2":"R+TFFQKIkQVPuKV4UsXJsobbGGNIhy8rpVnKKxCDW74uc+nO5pnosGaPUcdaYtf5MCn9b2ggJuzZt0mAOfTEnQo0doAtNAnw"},"s3":{"s3SchemaVersion":"1.0","configurationId":"di-s3-test-event-jpeg","bucket":{"name":"di-s3-test","ownerIdentity":{"principalId":"A356GIRQLABBUV"},"arn":"arn:aws:s3:::di-s3-test"},"object":{"key":"GEJFAE_CAMERA_3_20210430172504.jpeg","size":786750,"eTag":"47b583013eadea6b44dc29a7388a821e","sequencer":"00608BF213CC151FF4"}}}]}'}], 'ResponseMetadata': {'RequestId': '85865d84-5c27-50b7-b87c-048d985b17c5', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '85865d84-5c27-50b7-b87c-048d985b17c5', 'date': 'Mon, 03 May 2021 09:28:28 GMT', 'content-type': 'text/xml', 'content-length': '2061'}, 'RetryAttempts': 0}}
    for message in response['Messages']:
        body = json.loads(message['Body'])
        picture_id = body['meta_data']['picture_id']
    return response_list


def send_sqs_messages():
    sqs_client = boto3.client('sqs')
    s3_client = boto3.client('s3')
    images = s3_client.list_objects(
        Bucket='di-s3-cpl-idm-images',
        EncodingType='url',
        MaxKeys=100
    )
    for image in images['Contents']:
        print('images', image['Key'])
        message_json = {'image_path': image['Key'], 'bucket_name': 'di-s3-cpl-idm-images'}
        print('message_json', message_json)
        sqs_client.send_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/386826140800/di-sqs-cpl-idm',
            MessageBody=json.dumps(message_json),
        )
    return True

