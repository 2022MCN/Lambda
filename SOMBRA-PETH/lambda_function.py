import json
from PETH import *

def lambda_handler(event, context):
    
    db_name = event['teamName']
    table_name = event['tableName']
    print(db_name)
    print(table_name)
    

    match_id = table_name[0:13]
    map = table_name.split('_')[2]
    period = 10
    
    UU = PETH(db_name, map, match_id, period)

    event_name='UltimatesUsed/s'
    threshold=1
    print(db_name, table_name, event_name)

    UU.set_search_condition(event_name, threshold)
    UU.export_to_sql()

    CD1 = PETH(db_name, map, match_id, period)

    event_name='Cooldown1%/s'
    threshold=0.01
    print(db_name, table_name, event_name)
    CD1.set_search_condition(event_name, threshold)
    CD1.export_to_sql()

    CD2 = PETH(db_name, map, match_id, period)

    event_name='Cooldown2%/s'
    print(db_name, table_name, event_name)
    threshold=0.01
    CD2.set_search_condition(event_name, threshold)
    CD2.export_to_sql()

    CD3 = PETH(db_name, map, match_id, period)

    event_name='CooldownSecondaryFire%/s'
    print(db_name, table_name, event_name)
    threshold=0.01
    CD3.set_search_condition(event_name, threshold)
    CD3.export_to_sql()

    CD4 = PETH(db_name, map, match_id, period)

    event_name='CooldownCrouching%/s'
    print(db_name, table_name, event_name)
    threshold=0.01
    CD4.set_search_condition(event_name, threshold)
    CD4.export_to_sql()
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
