import os

class mysql_auth: 
    auth_info = {
        'hostname': 'localhost',
        'username': 'root',
        'pwd': 'knight4995_',
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