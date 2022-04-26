import json
from urllib import parse
from ScrimLog import *

def lambda_handler():#event, context):
    teamName = event['teamName']
    tableName = event['fileName'].split('.txt')[0]
    scrim_sql = ScrimLog().update_FinalStat_to_sql(teamName, tableName)
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps('Queued tables are successfully exported on Finalstat')
    }

lambda_handler()