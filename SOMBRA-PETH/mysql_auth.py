import os

class mysql_auth: 
    auth_info = {
        'hostname': os.environ['sombra_mysql_auth_host'],
        'username': os.environ['sombra_mysql_auth_user'],
        'pwd': os.environ['sombra_mysql_auth_passwd'],
        'port': int(os.environ['sombra_mysql_auth_port'])
    }