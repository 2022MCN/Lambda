from sqlalchemy import create_engine 
import pandas as pd 
from mysql_auth import mysql_auth


dstDB_login = mysql_auth.auth_info # import dstDB_login auth info

class MySQLConnection():
    def __init__(self, dbname, input_df=None, hostname=dstDB_login['hostname'], username=dstDB_login['username'], pwd=dstDB_login['pwd'], port=dstDB_login['port']):
        if input_df is None: 
            pass 

        # define input_df
        self.input_df = input_df
        # dbname
        self.dbname = dbname
        # create engine
        self.engine = create_engine('mysql+pymysql://' + username + ':' + pwd + '@' + hostname + ':' + str(port) + '/' + dbname , echo=False)

    def export_to_db(self, table_name, if_exists='append'):
        table_name = table_name.lower() 
        self.input_df.to_sql(name=table_name, con=self.engine, schema=self.dbname, index=False, if_exists=if_exists) # if_exsits:{'fail', 'replace', 'append'}

    def get_table_names(self):
        table_names = self.engine.table_names()
        
        return table_names

    def read_table_as_df(self, table_name):
        table_df = pd.read_sql(
            sql=f"SELECT * FROM `{table_name}`",
            con=self.engine,
        )
        if 'index' in table_df.columns.tolist():
            table_df.drop(columns='index', inplace=True) # drop 'index' column
        elif 'level_0' in table_df.columns.tolist():
            table_df.drop(columns='level_0', inplace=True) # drop 'level_0 column

        return table_df

