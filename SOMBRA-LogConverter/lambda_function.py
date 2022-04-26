import json
import os
import boto3
from urllib import parse

def lambda_handler(event, context):
    date = parse.unquote_plus(event['queryStringParameters']['date'])
    teamName = parse.unquote_plus(event['queryStringParameters']['teamName'])
    fileName = parse.unquote_plus(event['queryStringParameters']['fileName'])
    invoke_json_object = {
        'teamName': teamName,
        'fileName': fileName,
        'date': date
    }
    
    connect_finalstat = boto3.client(service_name='lambda', region_name='ap-northeast-2')
    connect_finalstat.invoke(FunctionName="SOMBRA-SaveRawdataToDB", InvocationType='Event', Payload=json.dumps(invoke_json_object))
    
    return {
    "statusCode": 200,
    'headers': {'Access-Control-Allow-Origin': '*'},
    "body": json.dumps("Successfully exported to database")
    }
    