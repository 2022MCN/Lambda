import pymysql
from mysqlAuth import MysqlAuth
from logDataStruct import LogPattern, MatchInfo, PlayerData, deltaX
from google.cloud import storage
from mapInfo import Controls, Maps
from UserAbbr import userabbr, convertUserName, setTeamName
        
class LogHandler: # Log Parsing & Handling
    def __init__(self, teamName, fileName, text):
        auth = MysqlAuth.auth_info
        self.teamName = teamName
        self.dbName = 'mcn_rawdb'
        self.logtext = text
        self.fileName = fileName
        self.logpattern = LogPattern()
        self.matchInfo = MatchInfo()
        self.playerList = []
        self.initialTimestamp = 0
        self.Maps = Maps()
        self.playerDataDict = {}   
        self.team1OffenseFlag = 'False'
        self.sectionNumber = 0
        self.mysqlConnection = pymysql.connect(host=auth['host'], user=auth['user'], password=auth['password'], port=auth['port'], db=self.dbName)
        self.cursor = self.mysqlConnection.cursor()
        self.deltaX: dict = {}
    
    def __del__(self):
        print('finished')
        self.mysqlConnection.close()

    def set_map_type(self):
        if self.matchInfo.Map in self.Maps.control:
            self.matchInfo.MapType = 'Control'
        elif self.matchInfo.Map in self.Maps.push:
            self.matchInfo.MapType = 'Push'
        elif self.matchInfo.Map in self.Maps.hybrid:
            self.matchInfo.MapType = 'Hybrid'
        elif self.matchInfo.Map in self.Maps.escort:
            self.matchInfo.MapType = 'Escort'
           
    def log_handler(self):
        mapname = self.logtext[0][11:].split(',')[0]
        self.create_table(mapname)
        for line in self.logtext:
            basket_list = self.define_basket_list(line)
            if self.logpattern.pattern_playerData.match(line):    # pattern 3 : Player Match data
                self.playerData_stream_handler(basket_list)
                self.boolean_handler(basket_list)
                player = convertUserName(line[11:].split(',')[1])
                self.export_to_db(player)
            
            elif self.logpattern.pattern_matchInfo.match(line):       # pattern 1 : MatchInfo
                self.matchInfo_stream_handler(basket_list)

            elif self.logpattern.pattern_playerInfo.match(line):    # pattern 2 : PlayerInfo
                self.playerInfo_stream_handler(basket_list)                    
                
            elif self.logpattern.pattern_finalblows.match(line):    # pattern 4 : Final blow occured(handling DeathBy* variables), need to clear the DeathBy series after write to csv
                self.finalBlows_stream_handler(basket_list)

            elif self.logpattern.pattern_typeControl.match(line): # pattern 5 : handling 'Point' and 'RoundMap' if the map type is control
                self.typeControl_stream_handler(basket_list)

            elif self.logpattern.pattern_typeOthers.match(line): # pattern 6 : handling 'Point' and 'RoundMap' if the map type is not control
                self.typeOthers_stream_handler(basket_list)

            elif self.logpattern.pattern_dupstart.match(line): # pattern 7 : handling echo ult
                self.dupstart_stream_handler(basket_list)

            elif self.logpattern.pattern_dupend.match(line): # pattern 7 : handling echo ult
                self.dupend_stream_handler(basket_list)

            elif self.logpattern.pattern_resurrect.match(line): #pattern 8 : resurrect
                self.resurrect_stream_handler(basket_list)
        
        return self.fileName

    def matchInfo_stream_handler(self,basket_list): # set MatchInfo Class
        self.matchInfo.Map = basket_list[0]
        self.matchInfo.Team_1 = basket_list[1]
        self.matchInfo.Team_2 = basket_list[2]
        self.matchInfo.Round = basket_list[3]
        if len(basket_list) == 5:
            self.matchInfo.Version = basket_list[4]
        elif len(basket_list) == 4:
            self.matchInfo.Version = 2.10
        print(self.matchInfo.Version)
        self.matchInfo.Section = str(int(self.matchInfo.Section) + 1)
        self.set_map_type()
        
        if self.matchInfo.MapType == 'Control':
            maplists = Controls()
            if self.matchInfo.Map == 'Ilios':
                self.matchInfo.RoundName = maplists.ilios[int(self.matchInfo.Round)]
            if self.matchInfo.Map == 'Lijiang Tower':
                self.matchInfo.RoundName = maplists.lijiang_tower[int(self.matchInfo.Round)]
            if self.matchInfo.Map == 'Oasis':
                self.matchInfo.RoundName = maplists.oasis[int(self.matchInfo.Round)]
            if self.matchInfo.Map == 'Busan':
                self.matchInfo.RoundName = maplists.busan[int(self.matchInfo.Round)]
            if self.matchInfo.Map == 'Nepal':
                self.matchInfo.RoundName = maplists.nepal[int(self.matchInfo.Round)]
        else:
            self.matchInfo.Offense = self.matchInfo.Team_2
            self.matchInfo.Defense = self.matchInfo.Team_1

    def playerInfo_stream_handler(self,basket_list): # define playerDataDict dictionary(type : {str, dict PlayerData}), and also set player name on PlayerData dict
        self.playerList = basket_list
        for i in range(0, len(self.playerList)):
            player = convertUserName(self.playerList[i])
            self.playerList[i] = player
            self.playerDataDict[player] = PlayerData()
            self.playerDataDict[player].Player = player
        team_one, team_two = setTeamName(basket_list)
        self.matchInfo.Team_1 = team_one
        self.matchInfo.Team_2 = team_two
        print(team_one, basket_list[0:5])
        print(team_two, basket_list[5:10])
    
    def playerData_stream_handler(self,basket_list): # set playerDataDict dictonary(type : {str, dict PlayerData})
        userProfile = convertUserName(basket_list[1])
        if self.initialTimestamp == 0:
            self.initialTimestamp = float(basket_list[0])
        self.playerDataDict[userProfile].Map = self.matchInfo.Map
        self.playerDataDict[userProfile].Version = self.matchInfo.Version

        if self.matchInfo.MapType != 'Control':
            self.playerDataDict[userProfile].Section = str(self.sectionNumber)
        else:
            self.playerDataDict[userProfile].Section = self.matchInfo.Section

        self.playerDataDict[userProfile].Timestamp = str(round(float(basket_list[0]) - self.initialTimestamp,2))

        if userProfile in self.playerList[0:5]: # set team
            self.playerDataDict[userProfile].Team = self.matchInfo.Team_1
        else:
            self.playerDataDict[userProfile].Team = self.matchInfo.Team_2

        if self.matchInfo.MapType == 'Control': # set map info
            self.playerDataDict[userProfile].RoundName = self.matchInfo.RoundName
        else:
            if userProfile in self.playerList[0:5]:
                if self.team1OffenseFlag == 'False':
                    self.playerDataDict[userProfile].RoundName = 'Defense'
                elif self.team1OffenseFlag == 'True':
                    self.playerDataDict[userProfile].RoundName = 'Offense'
            else:
                self.playerDataDict[userProfile].Team = self.matchInfo.Team_2
                if self.team1OffenseFlag == 'False':
                    self.playerDataDict[userProfile].RoundName = 'Offense'
                elif self.team1OffenseFlag == 'True':
                    self.playerDataDict[userProfile].RoundName = 'Defense'
        hero = ''
        if basket_list[2] != 'Lúcio' and basket_list[2] != 'Torbjörn':
            hero = basket_list[2]
        elif basket_list[2] == 'Lúcio':
            hero = 'Lucio'
        elif basket_list[2] == 'Torbjörn':
            hero = 'Torbjorn'
            
        if basket_list[2] == '':
            hero = self.playerDataDict[userProfile].Hero
            
        if float(self.playerDataDict[userProfile].HeroDamageDealt) <= float(basket_list[3]):
            self.playerDataDict[userProfile].HeroDamageDealt = basket_list[3]
            self.playerDataDict[userProfile].BarrierDamageDealt = basket_list[4]
            self.playerDataDict[userProfile].DamageBlocked = basket_list[5]
            self.playerDataDict[userProfile].DamageTaken = basket_list[6]
            self.playerDataDict[userProfile].Deaths = basket_list[7]
            self.playerDataDict[userProfile].Eliminations = basket_list[8]
            self.playerDataDict[userProfile].FinalBlows = str(int(basket_list[9]) + int(basket_list[11]))
            self.playerDataDict[userProfile].EnvironmentalDeaths = basket_list[10]
            self.playerDataDict[userProfile].EnvironmentalKills = basket_list[11]
            self.playerDataDict[userProfile].HealingDealt = basket_list[12]
            self.playerDataDict[userProfile].ObjectiveKills = basket_list[13]
            self.playerDataDict[userProfile].SoloKills = basket_list[14]
            self.playerDataDict[userProfile].UltimatesEarned = basket_list[15]
            self.playerDataDict[userProfile].UltimatesUsed = basket_list[16]
            self.playerDataDict[userProfile].HealingReceived = basket_list[17] # if workshop code gonna improved then we should have delete handling process about healingreceived
            self.playerDataDict[userProfile].DefensiveAssists = basket_list[31]
            self.playerDataDict[userProfile].OffensiveAssists = basket_list[32]
        else:
            print(basket_list)
            if userProfile not in self.deltaX:
                self.deltaX[userProfile] = deltaX()
            self.deltaX[userProfile].HeroDamageDealt = round(float(basket_list[3]) - float(self.deltaX[userProfile].HeroDamageDealt), 2)
            self.playerDataDict[userProfile].HeroDamageDealt = str(round(float(self.playerDataDict[userProfile].HeroDamageDealt) + self.deltaX[userProfile].HeroDamageDealt, 2))
            self.deltaX[userProfile].HeroDamageDealt = round(float(basket_list[3]), 2)

            self.deltaX[userProfile].BarrierDamageDealt = round(float(basket_list[4]) - float(self.deltaX[userProfile].BarrierDamageDealt), 2)
            self.playerDataDict[userProfile].BarrierDamageDealt = str(round(float(self.playerDataDict[userProfile].BarrierDamageDealt) + self.deltaX[userProfile].BarrierDamageDealt, 2))
            self.deltaX[userProfile].BarrierDamageDealt = round(float(basket_list[4]), 2)

            self.deltaX[userProfile].DamageBlocked = round(float(basket_list[5]) - float(self.deltaX[userProfile].DamageBlocked), 2)
            self.playerDataDict[userProfile].DamageBlocked = str(round(float(self.playerDataDict[userProfile].DamageBlocked) + self.deltaX[userProfile].DamageBlocked, 2))
            self.deltaX[userProfile].DamageBlocked = round(float(basket_list[5]), 2)

            self.deltaX[userProfile].DamageTaken = round(float(basket_list[6]) - float(self.deltaX[userProfile].DamageTaken), 2)
            self.playerDataDict[userProfile].DamageTaken = str(round(float(self.playerDataDict[userProfile].DamageTaken) + self.deltaX[userProfile].DamageTaken, 2))
            self.deltaX[userProfile].DamageTaken = round(float(basket_list[6]), 2)

            self.deltaX[userProfile].Deaths = int(basket_list[7]) - int(self.deltaX[userProfile].Deaths)
            self.playerDataDict[userProfile].Deaths = str(int(self.playerDataDict[userProfile].Deaths) + self.deltaX[userProfile].Deaths)
            self.deltaX[userProfile].Deaths = int(basket_list[7])

            self.deltaX[userProfile].Eliminations = int(basket_list[8]) - int(self.deltaX[userProfile].Eliminations)
            self.playerDataDict[userProfile].Eliminations = str(int(self.playerDataDict[userProfile].Eliminations) + self.deltaX[userProfile].Eliminations)
            self.deltaX[userProfile].Eliminations = int(basket_list[8])

            self.deltaX[userProfile].FinalBlows = int(basket_list[9]) + int(basket_list[11]) - int(self.deltaX[userProfile].FinalBlows)
            self.playerDataDict[userProfile].FinalBlows = str(int(self.playerDataDict[userProfile].FinalBlows) + self.deltaX[userProfile].FinalBlows)
            self.deltaX[userProfile].FinalBlows = int(basket_list[9])

            self.deltaX[userProfile].EnvironmentalDeaths = int(basket_list[10]) - int(self.deltaX[userProfile].EnvironmentalDeaths)
            self.playerDataDict[userProfile].EnvironmentalDeaths = str(int(self.playerDataDict[userProfile].EnvironmentalDeaths) + self.deltaX[userProfile].EnvironmentalDeaths)
            self.deltaX[userProfile].EnvironmentalDeaths = int(basket_list[10])

            self.deltaX[userProfile].EnvironmentalKills = int(basket_list[11]) - int(self.deltaX[userProfile].EnvironmentalKills)
            self.playerDataDict[userProfile].EnvironmentalKills = str(int(self.playerDataDict[userProfile].EnvironmentalKills) + self.deltaX[userProfile].EnvironmentalKills)
            self.deltaX[userProfile].EnvironmentalKills = int(basket_list[11])

            self.deltaX[userProfile].HealingDealt = round(float(basket_list[12]) - float(self.deltaX[userProfile].HealingDealt), 2)
            self.playerDataDict[userProfile].HealingDealt = str(round(float(self.playerDataDict[userProfile].HealingDealt) + self.deltaX[userProfile].HealingDealt, 2))
            self.deltaX[userProfile].HealingDealt = round(float(basket_list[12]), 2)

            self.deltaX[userProfile].ObjectiveKills = int(basket_list[13]) - int(self.deltaX[userProfile].ObjectiveKills)
            self.playerDataDict[userProfile].ObjectiveKills = str(int(self.playerDataDict[userProfile].ObjectiveKills) + self.deltaX[userProfile].ObjectiveKills)
            self.deltaX[userProfile].ObjectiveKills = int(basket_list[13])

            self.deltaX[userProfile].SoloKills = int(basket_list[14]) - int(self.deltaX[userProfile].SoloKills)
            self.playerDataDict[userProfile].SoloKills = str(int(self.playerDataDict[userProfile].SoloKills) + self.deltaX[userProfile].SoloKills)
            self.deltaX[userProfile].SoloKills = int(basket_list[14])


            self.deltaX[userProfile].UltimatesEarned = int(basket_list[15]) - int(self.deltaX[userProfile].UltimatesEarned)
            self.playerDataDict[userProfile].UltimatesEarned = str(int(self.playerDataDict[userProfile].UltimatesEarned) + self.deltaX[userProfile].UltimatesEarned)
            self.deltaX[userProfile].UltimatesEarned = int(basket_list[15])


            self.deltaX[userProfile].UltimatesUsed = int(basket_list[16]) - int(self.deltaX[userProfile].UltimatesUsed)
            self.playerDataDict[userProfile].UltimatesUsed = str(int(self.playerDataDict[userProfile].UltimatesUsed) + self.deltaX[userProfile].UltimatesUsed)
            self.deltaX[userProfile].UltimatesUsed = int(basket_list[16])


            self.deltaX[userProfile].HealingReceived = round(float(basket_list[17]) - float(self.deltaX[userProfile].HealingReceived), 2)
            self.playerDataDict[userProfile].HealingReceived = str(round(float(self.playerDataDict[userProfile].HealingReceived) + self.deltaX[userProfile].HealingReceived, 2)) # if workshop code gonna improved then we should have delete handling process about healingreceived
            self.deltaX[userProfile].HealingReceived = round(float(basket_list[17]), 2)


            self.deltaX[userProfile].DefensiveAssists = int(basket_list[31]) - int(self.deltaX[userProfile].DefensiveAssists)
            self.playerDataDict[userProfile].DefensiveAssists = str(int(self.playerDataDict[userProfile].DefensiveAssists) + self.deltaX[userProfile].DefensiveAssists)
            self.deltaX[userProfile].DefensiveAssists = int(basket_list[31])


            self.deltaX[userProfile].OffensiveAssists = int(basket_list[32]) - int(self.deltaX[userProfile].OffensiveAssists)
            self.playerDataDict[userProfile].OffensiveAssists = str(int(self.playerDataDict[userProfile].OffensiveAssists) + self.deltaX[userProfile].OffensiveAssists)
            self.deltaX[userProfile].OffensiveAssists = int(basket_list[32])
        
        self.playerDataDict[userProfile].Hero = hero
        self.playerDataDict[userProfile].UltimateCharge = basket_list[18]
        self.playerDataDict[userProfile].Position = basket_list[19] + ',' + basket_list[20] + ',' + basket_list[21]
        self.playerDataDict[userProfile].Cooldown1 = basket_list[23]
        self.playerDataDict[userProfile].Cooldown2 = basket_list[24]
        self.playerDataDict[userProfile].CooldownSecondaryFire = basket_list[25]
        self.playerDataDict[userProfile].CooldownCrouching = basket_list[26]
        self.playerDataDict[userProfile].IsAlive = basket_list[27]
        self.playerDataDict[userProfile].TimeElapsed = basket_list[28]
        self.playerDataDict[userProfile].MaxHealth = basket_list[29]
        self.playerDataDict[userProfile].Health = basket_list[30]
        self.playerDataDict[userProfile].IsBurning = basket_list[33]
        self.playerDataDict[userProfile].IsKnockedDown = basket_list[34]
        self.playerDataDict[userProfile].IsAsleep = basket_list[35]
        self.playerDataDict[userProfile].IsFrozen = basket_list[36]
        self.playerDataDict[userProfile].IsUnkillable = basket_list[37]
        self.playerDataDict[userProfile].IsInvincible = basket_list[38]
        self.playerDataDict[userProfile].IsHacked = basket_list[39]
        self.playerDataDict[userProfile].IsRooted = basket_list[40]
        self.playerDataDict[userProfile].IsStunned = basket_list[41]
        self.playerDataDict[userProfile].FacingDirection = basket_list[42] + ',' + basket_list[43] + ',' + basket_list[44]
        self.playerDataDict[userProfile].Team1Player1InViewAngle = basket_list[45]
        self.playerDataDict[userProfile].Team1Player2InViewAngle = basket_list[46]
        self.playerDataDict[userProfile].Team1Player3InViewAngle = basket_list[47]
        self.playerDataDict[userProfile].Team1Player4InViewAngle = basket_list[48]
        self.playerDataDict[userProfile].Team1Player5InViewAngle = basket_list[49]
        self.playerDataDict[userProfile].Team2Player1InViewAngle = basket_list[50]
        self.playerDataDict[userProfile].Team2Player2InViewAngle = basket_list[51]
        self.playerDataDict[userProfile].Team2Player3InViewAngle = basket_list[52]
        self.playerDataDict[userProfile].Team2Player4InViewAngle = basket_list[53]
        self.playerDataDict[userProfile].Team2Player5InViewAngle = basket_list[54].rstrip()

    def finalBlows_stream_handler(self,basket_list): # set DeathBy ... 
        userProfile = convertUserName(basket_list[2])
        victim = convertUserName(basket_list[3])
        self.playerDataDict[victim].DeathByPlayer = userProfile
        self.playerDataDict[victim].DeathByHero = self.playerDataDict[userProfile].Hero
        self.playerDataDict[victim].DeathByAbility = basket_list[4]
    
    def define_basket_list(self,line): # define basket list (delete [hh:mm:ss])
        basket_list = line[11:].split(',')
        basket_list[len(basket_list)-1] = basket_list[len(basket_list)-1].rstrip()
        return basket_list
    
    def boolean_handler(self, basket_list):
        userProfile = convertUserName(basket_list[1])

        if self.playerDataDict[userProfile].IsAlive == 'True':
            self.playerDataDict[userProfile].IsAlive = '1'
        elif self.playerDataDict[userProfile].IsAlive == 'False':
            self.playerDataDict[userProfile].IsAlive = '0'
        
        if self.playerDataDict[userProfile].IsBurning == 'True':
            self.playerDataDict[userProfile].IsBurning = '1'
        elif self.playerDataDict[userProfile].IsBurning == 'False':
            self.playerDataDict[userProfile].IsBurning = '0'
        
        if self.playerDataDict[userProfile].IsKnockedDown == 'True':
            self.playerDataDict[userProfile].IsKnockedDown = '1'
        elif self.playerDataDict[userProfile].IsKnockedDown == 'False':
            self.playerDataDict[userProfile].IsKnockedDown = '0'

        if self.playerDataDict[userProfile].IsFrozen == 'True':
            self.playerDataDict[userProfile].IsFrozen = '1'
        elif self.playerDataDict[userProfile].IsFrozen == 'False':
            self.playerDataDict[userProfile].IsFrozen = '0'
        
        if self.playerDataDict[userProfile].IsUnkillable == 'True':
            self.playerDataDict[userProfile].IsUnkillable = '1'
        elif self.playerDataDict[userProfile].IsUnkillable== 'False':
            self.playerDataDict[userProfile].IsUnkillable = '0'
        
        if self.playerDataDict[userProfile].IsInvincible == 'False':
            self.playerDataDict[userProfile].IsInvincible = '0'
        elif self.playerDataDict[userProfile].IsInvincible == 'True':
            self.playerDataDict[userProfile].IsInvincible = '1'

        if self.playerDataDict[userProfile].IsAsleep == 'True':
            self.playerDataDict[userProfile].IsAsleep = '1'
        elif self.playerDataDict[userProfile].IsAsleep== 'False':
            self.playerDataDict[userProfile].IsAsleep = '0'

        if self.playerDataDict[userProfile].IsRooted == 'True':
            self.playerDataDict[userProfile].IsRooted = '1'
        elif self.playerDataDict[userProfile].IsRooted== 'False':
            self.playerDataDict[userProfile].IsRooted = '0'        

        if self.playerDataDict[userProfile].IsStunned == 'True':
            self.playerDataDict[userProfile].IsStunned = '1'
        elif self.playerDataDict[userProfile].IsStunned == 'False':
            self.playerDataDict[userProfile].IsStunned = '0'        

        if self.playerDataDict[userProfile].IsHacked == 'True':
            self.playerDataDict[userProfile].IsHacked = '1'        
        elif self.playerDataDict[userProfile].IsHacked == 'False':
            self.playerDataDict[userProfile].IsHacked = '0'

        if self.playerDataDict[userProfile].Team1Player1InViewAngle == 'true' or self.playerDataDict[userProfile].Team1Player1InViewAngle == 'True':
            self.playerDataDict[userProfile].Team1Player1InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team1Player1InViewAngle == 'false' or self.playerDataDict[userProfile].Team1Player1InViewAngle == 'False':
            self.playerDataDict[userProfile].Team1Player1InViewAngle = '0'

        if self.playerDataDict[userProfile].Team1Player2InViewAngle == 'true' or self.playerDataDict[userProfile].Team1Player2InViewAngle == 'True':
            self.playerDataDict[userProfile].Team1Player2InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team1Player2InViewAngle == 'false' or self.playerDataDict[userProfile].Team1Player2InViewAngle == 'False':
            self.playerDataDict[userProfile].Team1Player2InViewAngle = '0'   

        if self.playerDataDict[userProfile].Team1Player3InViewAngle == 'true' or self.playerDataDict[userProfile].Team1Player3InViewAngle == 'True':
            self.playerDataDict[userProfile].Team1Player3InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team1Player3InViewAngle == 'false' or self.playerDataDict[userProfile].Team1Player3InViewAngle == 'False':
            self.playerDataDict[userProfile].Team1Player3InViewAngle = '0'   

        if self.playerDataDict[userProfile].Team1Player4InViewAngle == 'true' or self.playerDataDict[userProfile].Team1Player4InViewAngle == 'True':
            self.playerDataDict[userProfile].Team1Player4InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team1Player4InViewAngle == 'false' or self.playerDataDict[userProfile].Team1Player4InViewAngle == 'False':
            self.playerDataDict[userProfile].Team1Player4InViewAngle = '0'   

        if self.playerDataDict[userProfile].Team1Player5InViewAngle == 'true' or self.playerDataDict[userProfile].Team1Player5InViewAngle == 'True':
            self.playerDataDict[userProfile].Team1Player5InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team1Player5InViewAngle == 'false' or self.playerDataDict[userProfile].Team1Player5InViewAngle == 'False':
            self.playerDataDict[userProfile].Team1Player5InViewAngle = '0'   

        if self.playerDataDict[userProfile].Team2Player1InViewAngle == 'true' or self.playerDataDict[userProfile].Team2Player1InViewAngle == 'True':
            self.playerDataDict[userProfile].Team2Player1InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team2Player1InViewAngle == 'false' or self.playerDataDict[userProfile].Team2Player1InViewAngle == 'False':
            self.playerDataDict[userProfile].Team2Player1InViewAngle = '0'   

        if self.playerDataDict[userProfile].Team2Player2InViewAngle == 'true' or self.playerDataDict[userProfile].Team2Player2InViewAngle == 'True':
            self.playerDataDict[userProfile].Team2Player2InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team2Player2InViewAngle == 'false' or self.playerDataDict[userProfile].Team2Player2InViewAngle == 'False':
            self.playerDataDict[userProfile].Team2Player2InViewAngle = '0'   

        if self.playerDataDict[userProfile].Team2Player3InViewAngle == 'true' or self.playerDataDict[userProfile].Team2Player3InViewAngle == 'True':
            self.playerDataDict[userProfile].Team2Player3InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team2Player3InViewAngle == 'false' or self.playerDataDict[userProfile].Team2Player3InViewAngle == 'False':
            self.playerDataDict[userProfile].Team2Player3InViewAngle = '0'   

        if self.playerDataDict[userProfile].Team2Player4InViewAngle == 'true' or self.playerDataDict[userProfile].Team2Player4InViewAngle == 'True':
            self.playerDataDict[userProfile].Team2Player4InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team2Player4InViewAngle == 'false' or self.playerDataDict[userProfile].Team2Player4InViewAngle == 'False':
            self.playerDataDict[userProfile].Team2Player4InViewAngle = '0'   

        if self.playerDataDict[userProfile].Team2Player5InViewAngle == 'true' or self.playerDataDict[userProfile].Team2Player5InViewAngle == 'True':
            self.playerDataDict[userProfile].Team2Player5InViewAngle = '1'        
        elif self.playerDataDict[userProfile].Team2Player5InViewAngle == 'false' or self.playerDataDict[userProfile].Team2Player5InViewAngle == 'False':
            self.playerDataDict[userProfile].Team2Player5InViewAngle = '0'    

    def create_table(self, mapname):
        filename = self.fileName.split('.txt')[0] + '_' + mapname.lower()
        self.fileName = filename
        valid_check_query = "SELECT * FROM information_schema.tables WHERE table_schema = \"" + self.dbName +  "\" AND table_name = \"" + filename + "\""
        #print(valid_check_query)
        self.cursor.execute(valid_check_query)
        res = self.cursor.fetchall()
        if len(res) == 0 :
            pass
        else: 
            delete_table_query = "DROP TABLE `" + filename + '`'
            self.cursor.execute(delete_table_query)
        sql = 'CREATE TABLE `' + filename + '` (Map VARCHAR(100), Section INT, Point INT, RoundName VARCHAR(100), Timestamp FLOAT, Team VARCHAR(30), Player VARCHAR(30), Hero VARCHAR(30), HeroDamageDealt VARCHAR(10), BarrierDamageDealt VARCHAR(10), DamageBlocked VARCHAR(10), DamageTaken VARCHAR(10), Deaths VARCHAR(10), Eliminations VARCHAR(10), FinalBlows VARCHAR(10), EnvironmentalDeaths VARCHAR(10), EnvironmentalKills VARCHAR(10), HealingDealt VARCHAR(10), ObjectiveKills VARCHAR(10), SoloKills VARCHAR(10), UltimatesEarned VARCHAR(10), UltimatesUsed VARCHAR(10), HealingReceived VARCHAR(10), UltimateCharge VARCHAR(10), Cooldown1 VARCHAR(10), Cooldown2 VARCHAR(10), CooldownSecondaryFire VARCHAR(10), CooldownCrouching VARCHAR(10), IsAlive VARCHAR(10), Position VARCHAR(30), MaxHealth VARCHAR(10), DeathByHero VARCHAR(30), DeathByAbility VARCHAR(30), DeathByPlayer VARCHAR(30), Resurrected VARCHAR(30), DuplicatedHero VARCHAR(30), DuplicateStatus VARCHAR(30), Health VARCHAR(10), DefensiveAssists VARCHAR(10), OffensiveAssists VARCHAR(10), IsBurning VARCHAR(10), IsKnockedDown VARCHAR(10), IsInvincible VARCHAR(10), IsAsleep VARCHAR(10), IsFrozen VARCHAR(10), IsUnkillable VARCHAR(10), IsRooted VARCHAR(10), IsStunned VARCHAR(10), IsHacked VARCHAR(10), FacingDirection VARCHAR(30), Team1Player1InViewAngle BOOLEAN not null default 0, Team1Player2InViewAngle BOOLEAN not null default 0, Team1Player3InViewAngle BOOLEAN not null default 0, Team1Player4InViewAngle BOOLEAN not null default 0, Team1Player5InViewAngle BOOLEAN not null default 0, Team2Player1InViewAngle BOOLEAN not null default 0, Team2Player2InViewAngle BOOLEAN not null default 0, Team2Player3InViewAngle BOOLEAN not null default 0, Team2Player4InViewAngle BOOLEAN not null default 0, Team2Player5InViewAngle BOOLEAN not null default 0, Version DECIMAL(3,2) not null default 1.10);'
        try: 
            self.cursor.execute(sql)
        except Exception as e:
            print(e)
        finally:
            self.set_toFinalstatTable()
            self.mysqlConnection.commit()

    def set_toFinalstatTable(self):
        filename = self.fileName.split('.txt')[0]
        valid_check_query = "SELECT * FROM toFinalstatTable where tablename = \"" + filename + "\""
        self.cursor.execute(valid_check_query)
        res = self.cursor.fetchall()
        if len(res) == 0:
            sql = 'INSERT INTO toFinalstatTable (tablename) values (%s)'
            self.cursor.execute(sql, filename)
        else: 
            sql = "UPDATE toFinalstatTable SET isReflected = false WHERE tablename = \"" + filename + "\""
            self.cursor.execute(sql)
        self.mysqlConnection.commit()

    def export_to_db(self, player):
        tablename = '`' + self.fileName + '`'
        p = self.playerDataDict[player].__dict__
        sql = 'INSERT INTO ' + tablename + ' values (%(Map)s, %(Section)s, %(Point)s, %(RoundName)s, %(Timestamp)s, %(Team)s, %(Player)s, %(Hero)s, %(HeroDamageDealt)s, %(BarrierDamageDealt)s, %(DamageBlocked)s, %(DamageTaken)s, %(Deaths)s, %(Eliminations)s, %(FinalBlows)s, %(EnvironmentalDeaths)s, %(EnvironmentalKills)s, %(HealingDealt)s, %(ObjectiveKills)s, %(SoloKills)s, %(UltimatesEarned)s, %(UltimatesUsed)s, %(HealingReceived)s, %(UltimateCharge)s, %(Cooldown1)s, %(Cooldown2)s, %(CooldownSecondaryFire)s, %(CooldownCrouching)s, %(IsAlive)s, %(Position)s, %(MaxHealth)s, %(DeathByHero)s, %(DeathByAbility)s, %(DeathByPlayer)s, %(Resurrected)s, %(DuplicatedHero)s, %(DuplicateStatus)s, %(Health)s, %(DefensiveAssists)s, %(OffensiveAssists)s, %(IsBurning)s, %(IsKnockedDown)s, %(IsInvincible)s, %(IsAsleep)s, %(IsFrozen)s, %(IsUnkillable)s, %(IsRooted)s, %(IsStunned)s, %(IsHacked)s, %(FacingDirection)s, %(Team1Player1InViewAngle)s, %(Team1Player2InViewAngle)s, %(Team1Player3InViewAngle)s, %(Team1Player4InViewAngle)s, %(Team1Player5InViewAngle)s, %(Team2Player1InViewAngle)s, %(Team2Player2InViewAngle)s, %(Team2Player3InViewAngle)s, %(Team2Player4InViewAngle)s, %(Team2Player5InViewAngle)s, %(Version)s);'
        self.cursor.execute(sql, p)
        self.mysqlConnection.commit()
        self.cleansing_DeathBy(player)
        self.cleansing_resurrect(player)
    
    def cleansing_DeathBy(self,player):
        if self.playerDataDict[player].DeathByPlayer != '': 
            self.playerDataDict[player].DeathByPlayer = ''
        if self.playerDataDict[player].DeathByAbility != '':
            self.playerDataDict[player].DeathByAbility = ''
        if self.playerDataDict[player].DeathByHero != '':
            self.playerDataDict[player].DeathByHero = ''
    
    def cleansing_resurrect(self,player):
        if self.playerDataDict[player].Resurrected == 'RESURRECTED':
            self.playerDataDict[player].Resurrected = ''

    def typeControl_stream_handler(self,basket_list): # set point if the map is Control type
        for i in range(0, 5):
            self.playerDataDict[self.playerList[i]].Point = basket_list[1]
            self.playerDataDict[self.playerList[i+5]].Point = basket_list[2]
        
    def typeOthers_stream_handler(self,basket_list): # set point if the map is not Control type
        if basket_list[1] != self.team1OffenseFlag and self.matchInfo.MapType != 'Control':
            self.sectionNumber = self.sectionNumber + 1
        if basket_list[1] == 'False':
            self.team1OffenseFlag = 'False'            
            for i in range(0, 5):
                self.playerDataDict[self.playerList[i+5]].Point = basket_list[2]
        elif basket_list[1] == 'True':
            self.team1OffenseFlag = 'True'
            for i in range(0, 5):
                self.playerDataDict[self.playerList[i]].Point = basket_list[2]
    
   
    def dupstart_stream_handler(self,basket_list): # handling duplicate - duplicate ON
        userProfile = convertUserName(basket_list[2])
            
        hero = ''
        if basket_list[3] != 'Lúcio' and basket_list[3] != 'Torbjörn' :
            hero = basket_list[3]
        elif basket_list[3] == 'Lúcio':
            hero = 'Lucio'
        elif basket_list[3] == 'Torbjörn':
            hero = 'Torbjorn'
        self.playerDataDict[userProfile].DuplicateStatus = 'DUPLICATING'
        self.playerDataDict[userProfile].DuplicatedHero = hero
    
    def dupend_stream_handler(self,basket_list): # handling duplicate - duplicate OFF
        userProfile = convertUserName(basket_list[2])
        self.playerDataDict[userProfile].DuplicateStatus = ''
        self.playerDataDict[userProfile].DuplicatedHero = ''

    def resurrect_stream_handler(self, basket_list): # handling resurrect event
        userProfile = convertUserName(basket_list[2])
        self.playerDataDict[userProfile].Resurrected = 'RESURRECTED'
