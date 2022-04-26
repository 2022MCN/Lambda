import os

class MysqlAuth: 
    auth_info = {
        'host': 'localhost',
        'user': 'root',
        'password': 'knight4995_',
        'port': 3306
    }

'''
class MysqlAuth: 
    auth_info = {
        'host': 'draftify-sombra.cz0fsylbxfbk.ap-northeast-2.rds.amazonaws.com',
        'user': 'draftify',
        'password': 'c|NHAZbcG&WF(7U',
        'port': 3306
    }
'''

'''
class MysqlAuth: 
    auth_info = {
        'host': os.environ['sombra_mysql_auth_host'],
        'user': os.environ['sombra_mysql_auth_user'],
        'password': os.environ['sombra_mysql_auth_passwd'],
        'port': int(os.environ['sombra_mysql_auth_port'])
    }
'''
