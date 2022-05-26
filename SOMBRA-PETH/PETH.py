import pandas as pd
import numpy as np
import os
import time
from StatAbbr import *
from MySQLConnection import *
from sqlalchemy import exc
from MapNameList import *

class PETH():
    def __init__(self, db_name, map=None, match_id=None, period=10):
        self.db_name = db_name
        self.period = period
        if match_id is None or map is None:
            pass
        else:
            self.match_id = match_id
            self.map = map

    def set_df_init(self):
        db_name = self.db_name
        table_name = 'finalstat'
        match_id = self.match_id
        map = self.map

        sql = f'select * from {table_name} where `MatchId`="{match_id}" and `Map` = "{map}";'
        #print(sql)
        self.df_init = pd.read_sql(sql = sql, con = MySQLConnection(dbname = db_name).engine)
        self.timestamp_list = self.df_init['Timestamp'].drop_duplicates().tolist()
        #print(self.df_init)
        
    def set_search_condition(self, event_name=None, threshold=1):
        if event_name is None:
            pass
        else:
            self.event_name = event_name
            self.threshold = threshold
            self.stat_name_abbr = StatAbbr[self.event_name]
            self.set_PETH()

    def set_events(self):
        self.set_df_init()
        event_onset = self.df_init[self.df_init[self.event_name] >= self.threshold]
        return event_onset
        
    def get_nearest_timestamp(self, timestamp):
        for data in timestamp.drop_duplicates():
            min_diff = -1
            r_value = -1

            for val in self.timestamp_list:
                abs_diff = abs(val - data)

                if min_diff == -1 or min_diff > abs_diff:
                    min_diff = abs_diff
                    r_value  = val
            timestamp = timestamp.replace(to_replace=data, value=r_value)

        return timestamp

    def set_PETH(self):
        df_event_onset = self.set_events()
        
        if len(df_event_onset) == 0:
            df_PETH_res = pd.DataFrame({'MatchId':[], 'num_map':[], 'Map':[], 'Section':[], 'RoundName':[], 'num_Event':[], 'ref_Team':[], 'ref_Player':[], 'ref_Hero':[], 'ref_Event':[], 'Team':[], 'Player':[], 'Hero':[], 'Timestamp':[]})
        else:
            idx_col = ['MatchId', 'Map', 'Section', 'RoundName', 'Team', 'Player', 'Hero', 'Timestamp']
            num_Event = 0
            df_list = []
            for idx, row in df_event_onset.iterrows():
                num_Event += 1
                # set reference vars
                ref_match_id = row['MatchId']
                ref_map_name = row['Map']
                ref_timestamp = row['Timestamp']
                ref_team_name = row['Team']
                ref_player_name = row['Player']
                ref_hero_name = row['Hero']
                # PETH_timestamp
                # align FinalStat by event onset
                event_onset = row['Timestamp']
                df_event_recorder = self.df_init[(self.df_init['Timestamp'] >= (event_onset - (self.period + 1))) & (self.df_init['Timestamp'] <= (event_onset + (self.period + 1)))]
                df_event_recorder = df_event_recorder.copy() # make a copy to avoid SettingWithCopyWarning
                df_event_recorder['EventOnset'] = event_onset
                df_event_recorder['Timestamp'] -= event_onset
                df_event_recorder['Timestamp'] = df_event_recorder['Timestamp'].astype(int)
                
                # reference columns
                df_event_recorder['ref_Team'] = ref_team_name
                df_event_recorder['ref_Player'] = ref_player_name
                df_event_recorder['ref_Hero'] = ref_hero_name
                event_name = ''
                if self.event_name in tableAbbr:
                    event_name = tableAbbr[self.event_name]
                else:
                    event_name = self.event_name
                df_event_recorder['ref_Event'] = event_name
                #df_event_recorder['ref_Timestamp'] = ref_timestamp + df_event_recorder['Timestamp']
                df_event_recorder['ref_Timestamp'] = self.get_nearest_timestamp(ref_timestamp + df_event_recorder['Timestamp'])
                df_event_recorder['PETH_Timestamp'] = df_event_recorder['Timestamp']
                df_event_recorder['num_Event'] = num_Event 

                # concat
                df_list.append(df_event_recorder)

            df_PETH = pd.concat(df_list)            
            df_PETH_res = df_PETH[['MatchId', 'num_map', 'Map', 'Section', 'RoundName', 'num_Event', 'ref_Team', 'ref_Player', 'ref_Hero', 'ref_Event', 'ref_Timestamp', 'Team', 'Player', 'Hero', 'PETH_Timestamp']]
            df_PETH = df_PETH.set_index(['MatchId', 'num_map', 'Map', 'Section', 'RoundName', 'num_Event', 'ref_Team', 'ref_Player', 'ref_Hero', 'ref_Event', 'ref_Timestamp', 'Team', 'Player', 'Hero', 'PETH_Timestamp'])

        #df_PETH_res.to_csv('C:\\Users\\Sqix_OW\\Desktop\\Study\\DA Project\\practice\PETH\\skill_test.csv')
        self.df_PETH = df_PETH_res.reset_index(level=0, drop=True)

    def get_PETH(self):
        return self.df_PETH

    def export_to_csv(self):
        self.df_PETH.to_csv('C:\\Users\\Sqix_OW\\Desktop\\Study\\DA Project\\practice\PETH\\ult_test.csv')

    def export_to_sql(self):
        # multi-mod
        def get_update_list():
            sql_for_finalstat = f'select distinct MatchId, Map from finalstat;'
            sql_for_peth = f'select distinct MatchId, Map from peth;'
            df_finalstat_match_id_list = pd.read_sql(sql = sql_for_finalstat, con = MySQLConnection(dbname = self.db_name).engine).values.tolist()
            df_peth_match_id_list = pd.read_sql(sql = sql_for_peth, con = MySQLConnection(dbname = self.db_name).engine).values.tolist()
            update_list = [val for val in df_finalstat_match_id_list if val not in df_peth_match_id_list]
            return update_list
        # uni-mod
        #print(self.get_PETH())
        df_sql = MySQLConnection(input_df=self.get_PETH(), dbname=self.db_name)
        try:
            df_sql.export_to_db(table_name='peth', if_exists='append')
            print(f'File Exported: {self.event_name} Event, {self.match_id}, {self.map}')
        except exc.IntegrityError as e:
            print(f"Integrityerror: {e}")
'''
if __name__ == "__main__":
    starttime = time.time()
    db_name = 'Draftify'
    map = 'Colosseo'
    match_id = '220507_072322'
    period = 10

    UU = PETH(db_name, map, match_id, period)

    event_name='UltimatesUsed/s'
    threshold=1

    UU.set_search_condition(event_name, threshold)
    UU.export_to_sql()

    CD1 = PETH(db_name, map, match_id, period)

    event_name='Cooldown1%/s'
    threshold=0.01
    CD1.set_search_condition(event_name, threshold)
    CD1.export_to_sql()

    CD2 = PETH(db_name, map, match_id, period)

    event_name='Cooldown2%/s'
    threshold=0.01
    CD2.set_search_condition(event_name, threshold)
    CD2.export_to_sql()

    CD3 = PETH(db_name, map, match_id, period)

    event_name='CooldownSecondaryFire%/s'
    threshold=0.01
    CD3.set_search_condition(event_name, threshold)
    CD3.export_to_sql()

    CD4 = PETH(db_name, map, match_id, period)

    event_name='CooldownCrouching%/s'
    threshold=0.01
    CD4.set_search_condition(event_name, threshold)
    CD4.export_to_sql()

    print("time: ", time.time() - starttime)

'''