import json
import os
import pymysql
import boto3
from urllib import parse
from google.cloud import storage
from mysqlAuth import MysqlAuth
from logHandler import LogHandler

def lambda_handler():#event, context):
    
    #teamName = event['teamName']
    #fileName = event['fileName']
    #date = event['date']
    
    teamName = 'Guangzhou Charge'
    #fileName = 'Log-2022-05-03-14-05-35.txt'
    #date = '220503_140535'
    
    # push to mcn
    storageClient = storage.Client.from_service_account_json('./serviceAccountKey.json')
    bucketName = 'esports-social-media.appspot.com'
    blobs = storageClient.list_blobs(bucketName)
    #targetFileName = teamName + '/' + fileName
    
    for blob in blobs:
        print(blob.name)
        if blob.name.split('/')[0] == 'Guangzhou Charge' and blob.name.split('/')[1] != '':
            text = blob.download_as_text(client = storageClient)
            print("Blob: {}".format(blob.name))
            print("bucket: {}".format(blob.bucket.name))
            date = str(blob.updated)
            file_name = date.split(' ')[0].split('-')[0] + date.split(' ')[0].split('-')[1] + date.split(' ')[0].split('-')[2] + '_' + date.split(' ')[1].split(':')[0] + date.split(' ')[1].split(':')[1] + date.split(' ')[1].split(':')[2].split('.')[0]
            print(file_name)
            #i = input()
            text = text.splitlines()
            parser = LogHandler(teamName, file_name, text)
            finalstat_file_name = parser.log_handler()
    
    #file_name = date
    
    '''
    #push to localhost db
    storageClient = storage.Client.from_service_account_json('./serviceAccountKey.json')
    bucketName = 'esports-social-media.appspot.com'
    blobs = storageClient.list_blobs(bucketName)
    targetFileName = teamName + '/' + fileName
    for blob in blobs:
        if targetFileName == blob.name:
            text = blob.download_as_text(client = storageClient)
            break
    text = text.splitlines()
    file_name = '' + date.split('T')[0].split('-')[0][2] + date.split('T')[0].split('-')[0][3] + date.split('T')[0].split('-')[1][0] + date.split('T')[0].split('-')[1][1] + date.split('T')[0].split('-')[2][0] + date.split('T')[0].split('-')[2][1] + '_'
    file_name = file_name + date.split('T')[1].split(':')[0][0] + date.split('T')[1].split(':')[0][1] + date.split('T')[1].split(':')[1][0] + date.split('T')[1].split(':')[1][1] + date.split('T')[1].split(':')[2][0] + date.split('T')[1].split(':')[2][1] + '.txt'
    
    file_name = date
    parser = LogHandler(teamName, file_name, text)
    finalstat_file_name = parser.log_handler()
    '''
    '''
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
    '''
    
lambda_handler()