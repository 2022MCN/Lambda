import os

class mysql_auth: 
    auth_info = {
        'hostname': 'draftify-sombra.cz0fsylbxfbk.ap-northeast-2.rds.amazonaws.com',
        'username': 'draftify',
        'pwd': 'c|NHAZbcG&WF(7U',
        'port': 3306
}

'''
class mysql_auth: 
    auth_info = {
        'hostname': os.environ['sombra_mysql_auth_host'],
        'username': os.environ['sombra_mysql_auth_user'],
        'pwd': os.environ['sombra_mysql_auth_passwd'],
        'port': int(os.environ['sombra_mysql_auth_port'])
    }
'''