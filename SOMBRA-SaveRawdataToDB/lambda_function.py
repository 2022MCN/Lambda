import json
import os
import pymysql
import boto3
from urllib import parse
from google.cloud import storage
from mysqlAuth import MysqlAuth
from logHandler import LogHandler

def lambda_handler(event, context):
    
    teamName = event['teamName']
    fileName = event['fileName']
    storageClient = storage.Client.from_service_account_json('./serviceAccountKey.json')
    bucketName = 'esports-social-media.appspot.com'
    blobs = storageClient.list_blobs(bucketName)
    targetFileName = teamName + '/' + fileName
    text = ''
    for blob in blobs:
        if targetFileName == blob.name:
            text = blob.download_as_text(client = storageClient)
            break
    text = text.splitlines()
    parser = LogHandler(teamName, fileName, text)
    parser.log_handler()
    
    invoke_json_object = {
        'teamName': teamName,
        'fileName': fileName
    }
    
    connect_finalstat = boto3.client(service_name='lambda', region_name='ap-northeast-2')
    connect_finalstat.invoke(FunctionName="SOMBRA-finalstat", InvocationType='Event', Payload=json.dumps(invoke_json_object))
    
    successString = fileName + ' successfully uploaded on ' + teamName + ' storage!'
    return {
    "statusCode": 200,
    'headers': {'Access-Control-Allow-Origin': '*'},
    "body": json.dumps(successString)
    }
    