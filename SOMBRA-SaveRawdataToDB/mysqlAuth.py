import os

class MysqlAuth: 
    auth_info = {
        'host': os.environ['sombra_mysql_auth_host'],
        'user': os.environ['sombra_mysql_auth_user'],
        'password': os.environ['sombra_mysql_auth_passwd'],
        'port': int(os.environ['sombra_mysql_auth_port'])
    }
