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
    date = event['date']
    
    #teamName = 'T1'
    #fileName = '20220314_01_O2_Lijiang Tower.txt'
    
    storageClient = storage.Client.from_service_account_json('./serviceAccountKey.json')
    bucketName = 'esports-social-media.appspot.com'
    blobs = storageClient.list_blobs(bucketName)
    targetFileName = teamName + '/' + fileName
    for blob in blobs:
        if targetFileName == blob.name:
            text = blob.download_as_text(client = storageClient)
            break
    text = text.splitlines()
    print(text)
    
    file_name = '' + date.split('T')[0].split('-')[0][2] + date.split('T')[0].split('-')[0][3] + date.split('T')[0].split('-')[1][0] + date.split('T')[0].split('-')[1][1] + date.split('T')[0].split('-')[2][0] + date.split('T')[0].split('-')[2][1] + '_'
    file_name = file_name + date.split('T')[1].split(':')[0][0] + date.split('T')[1].split(':')[0][1] + date.split('T')[1].split(':')[1][0] + date.split('T')[1].split(':')[1][1] + date.split('T')[1].split(':')[2][0] + date.split('T')[1].split(':')[2][1] + '.txt'
    parser = LogHandler(teamName, file_name, text)
    finalstat_file_name = parser.log_handler()
    
    invoke_json_object = {
        'teamName': teamName,
        'fileName': finalstat_file_name
    }
    
    connect_finalstat = boto3.client(service_name='lambda', region_name='ap-northeast-2')
    connect_finalstat.invoke(FunctionName="SOMBRA-finalstat", InvocationType='Event', Payload=json.dumps(invoke_json_object))
    
    successString = fileName + ' successfully uploaded on ' + teamName + ' storage!'
    return {
    "statusCode": 200,
    'headers': {'Access-Control-Allow-Origin': '*'},
    "body": json.dumps(successString)
    }
    