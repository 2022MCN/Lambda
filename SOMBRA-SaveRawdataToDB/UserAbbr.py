import re
import sys
import smtplib
from email.mime.text import MIMEText


teamabbr : dict= {
    'Los Angeles Valiant': 'VAL',
    'Guangzhou Charge': 'GZC',
    'New York Excelsior': 'NYE',
    'Shanghai Dragons': 'SHD',
    'Seoul Dynasty': 'SEO',
    'Chengdu Hunters': 'CDH',
    'Philadelphia Fusions': 'PHI',
    'Hangzhou Spark': 'HZS',
    'Los Angeles Gladiators': 'GLA',
    'Dallas Fuel': 'DAL',
    'London Spitfire': 'LDN',
    'Vancouver Titans': 'VAN',
    'Boston Uprising': 'BOS',
    'San Francisco Shock': 'SFS',
    'Atlanta Reign': 'ATL',
    'Washington Justice': 'WAS',
    'Toronto Defiant': 'TOR',
    'Paris Eternal': 'PAR',
    'Florida Mayhem': 'FLA',
    'Houston Outlaws': 'HOU'
}

players_dict : dict= {
    'Los Angeles Valiant': ['Diya', 'Ezhan', 'INNOVATION', 'Becky', 'SASIN', 'Lengsa', 'ColdesT'],
    'Guangzhou Charge': ['Eileen', 'ChoiSehwan', 'Develop', 'Cr0ng', 'Rio', 'Unique', 'Molly', 'Farway1987'],
    'New York Excelsior': ['Flora', 'Yaki', 'Kellan', 'GangNamJin', 'Myunb0ng'],
    'Shanghai Dragons': ['Fleta', 'WhoRu', 'LIP', 'Fate', 'Void', 'LeeJaeGon', 'IZaYaKI', 'BEBE'],
    'Seoul Dynasty': ['Fits', 'Stalk3r', 'Profit', 'smurf', 'Creative', 'Vindaim'],
    'Chengdu Hunters': ['Leave', 'JinMu', 'Apr1ta', 'GA9A', 'Nisha', 'Yveltal', 'Mmonk'],
    'Philadelphia Fusions': ['MN3', 'ZEST', 'carpe', 'Belosrea', 'Fury', 'FiXa', 'AimGod'],
    'Hangzhou Spark': ['Pineapple', 'shy', 'Architect', 'AlphaYi', 'Guxue', 'BERNAR', 'LIGE', 'Irony', 'Haoyoqian'],
    'Los Angeles Gladiators': ['kevster', 'ANS', 'Patiphan', 'SPACE', 'Reiner', 'shu', 'FunnyAstro', 'skewed'],
    'Dallas Fuel': ['SP9RK1E', 'Edison', 'Doha', 'guriyo', 'FEARLESS', 'Hanbin', 'ChiYo', 'Fielder'],
    'London Spitfire': ['SparkR', 'Shax', 'Backbone', 'Hadi', 'Poko', 'Admiral', 'Landon'],
    'Vancouver Titans': ['Aspire', 'sHockWave', 'Seicoe', 'False', 'Masaa', 'Aztac', 'Skairipa'],
    'Boston Uprising': ['punk', 'Victoria', 'STRIKER', 'Valentine', 'Marve1', 'Faith', 'Crimzo', 'MCD'],
    'San Francisco Shock': ['Proper', 'Kilo', 's9mm', 'Coluge', 'FiNN', 'Viol2t'],
    'Atlanta Reign': ['Gator', 'Hawk', 'Kai', 'nero', 'Venom', 'Ojee', 'UltraViolet'],
    'Washington Justice': ['Decay', 'Mag', 'Assassin', 'Happy', 'Krillin', 'OPENER', 'Kalios', 'WAS004', 'WAS008', 'WAS003', 'WAS002', 'WAS017', 'WAS018'],
    'Toronto Defiant': ['Heesu', 'Twilight', 'HOTBA', 'CH0R0NG', 'MuZe', 'Finale', 'ALTHOUGH', 'TOR003', 'TOR005', 'TOR001', 'TOR006', 'TOR007', 'TOR002'],
    'Paris Eternal': ['Naga', 'Daan', 'Kaan', 'dridro', 'Glister', 'Vestola'],
    'Florida Mayhem': ['SirMajed', 'CheckMate', 'Adam', 'SOMEONE', 'Anamo', 'Hydron', 'KariV', 'Xzi'],
    'Houston Outlaws': ['Danteh', 'PIGGY', 'Pelican', 'Ir1s', 'Lastro', 'MER1T', 'HOU004', 'HOU001', 'HOU003', 'HOU006', 'HOU005', 'HOU002']
}

userabbr : dict = {
    '냐옹': 'Yaki',
    'nuGget': 'Vulcan',
    'Myun****': 'Myunb0ng',
    '한강돗자리도둑': 'Glister',
    'ANAMO': 'Anamo',
    'NYE029': 'Vulcan',
    'NYE004': 'Kellan',
    'NYE010': 'GangNamJin',
    'NYE005': 'Yaki',
    'NYE008': 'Myunb0ng',
    'NYE006': 'Flora',
    'SFS020': 'Kilo',
    'SFS007': 'Proper',
    'SFS023': 'Coluge',
    'SFS001': 'FiNN',
    'SFS017': 'Viol2t',
    'SFS013': 's9mm',
    'GZC002': 'Farway1987',
    'GZC004': 'Rio',
    'GZC005': 'Cr0ng',
    'GZC006': 'ChoiSehwan',
    'GZC007': 'Develop',
    'GZC008': 'Eileen',
    'GZC009': 'Molly',
    'GZC010': 'Unique',
    'SHD001': 'Void',
    'SHD002': 'Fate',
    'SHD005': 'Fleta',
    'SHD003': 'LIP',
    'SHD006': 'IZaYaKI',
    'SHD009': 'LeeJaeGon',
    'SHD004': 'WhoRu',
    'BOS008': 'Valentine',
    'BOS020': 'MCD',
    'BOS021': 'punk',
    'BOS007': 'STRIKER',
    'BOS009': 'Victoria',
    'BOS023': 'Marve1',
    'BOS002': 'ITSAL',
    'BOS012': 'Faith',
    'BOS013': 'Crimzo',
    'VAN020': 'Seicoe',
    'VAN012': 'Aspire',
    'VAN027': 'False',
    'VAN028': 'Skairipa',
    'VAN008': 'Masaa',
    'VAN029': 'Aztac',
    'HZS011': 'BERNAR',
    'HZS027': 'AlphaYi',
    'HZS022': 'shy',
    'HZS020': 'HAOYOQIAN',
    'HZS010': 'Irony',
    'HZS008': 'Guxue',
    'HZS015': 'Pineapple',
    'HZS001': 'Architect',
    'HZS005': 'LIGE',
    'CDH007': 'GA9A',
    'CDH002': 'Leave',
    'CDH026': 'JinMu',
    'CDH010': 'Nisha',
    'CDH013': 'Mmonk',
    'PHI004': 'Fury',
    'PHI005': 'Belosrea',
    'PHI002': 'carpe',
    'PHI003': 'ZEST',
    'PHI011': 'MN3',
    'PHI006': 'FiXa',
    'PHI007': 'AimGod',
    'PAR016': 'Naga',
    'PAR021': 'Glister',
    'PAR006': 'Vestola',
    'PAR011': 'dridro',
    'PAR001': 'Kaan',
    'PAR007': 'Daan',
    'LDN001': 'Hadi',
    'LDN006': 'Landon',
    'LDN007': 'Admiral',
    'LDN003': 'Backbone',
    'LDN005': 'LDN005',
    'LDN004': 'LDN004',
    'LDN002': 'Poko',
    'HOU004': 'MER1T',
    'HOU001': 'Pelican',
    'HOU003': 'Danteh',
    'HOU006': 'Ir1s',
    'HOU005': 'Lastro',
    'HOU002': 'PIGGY',
    'WAS004': 'Mag',
    'WAS008': 'OPENER',
    'WAS003': 'Decay',
    'WAS002': 'Happy',
    'WAS017': 'Krillin',
    'WAS018': 'Kalios',
    'TOR003': 'Heesu',
    'TOR005': 'Finale',
    'TOR001': 'MuZe',
    'TOR006': 'CH0R0NG',
    'TOR007': 'Twilight',
    'TOR002': 'HOTBA',
    'SEO029': 'smurf',
    'SEO003': 'Vindaim',
    'SEO011': 'Creative',
    'SEO001': 'Fits',
    'SEO002': 'Profit',
    'SEO013': 'Stalk3r'
}

'''
    for teamname in teamabbr:
        if userProfile in teamabbr[teamname]:
            print(teamname)
'''

def setTeamName(basket_list):
    for i in range(0, len(basket_list)):
        basket_list[i] = convertUserName(basket_list[i])
    team_1 = []
    team_2 = []
    players_dict_lower: dict = {} 
    for s in players_dict:
        players_dict_lower[s] = [t.lower() for t in players_dict[s]]

    for i in range(0, int(len(basket_list) / 2)):
        flag = False
        for teamname in players_dict_lower:
            if basket_list[i].lower() in players_dict_lower[teamname]:
                team_1.append(teamname)
                flag = True
                break
        if flag == False:
            team_1.append('Mercenary')
            
    for i in range(int(len(basket_list) / 2), len(basket_list)):
        flag = False
        for teamname in players_dict_lower:
            if basket_list[i].lower() in players_dict_lower[teamname]:
                team_2.append(teamname)
                flag = True
                break
        if flag == False:
            team_2.append('Mercenary')
    team_one_count: dict = {}
    for team_one_counter in team_1:
        if team_one_counter not in team_one_count:
            team_one_count[team_one_counter] = 1
            continue        
        if team_one_counter in team_one_count:
            team_one_count[team_one_counter] += 1
            continue

    team_two_count: dict = {}
    for team_two_counter in team_2:
        if team_two_counter not in team_two_count:
            team_two_count[team_two_counter] = 1
            continue
        if team_two_counter in team_two_count:
            team_two_count[team_two_counter] += 1
            continue

    team_one_max = max(team_one_count,key=team_one_count.get)
    team_two_max = max(team_two_count,key=team_two_count.get)
    team_one = team_one_max
    team_two = team_two_max

    if team_one_count[team_one_max] == 2:
        team_one = 'Undefined'
        sendErrorMail()
        sys.exit('Undefined Team Error')

    if team_two_count[team_two_max] == 2:
        team_two = 'Undefined'
        sendErrorMail()
        sys.exit('Undefined Team Error')
        
        
    team_one = teamabbr[team_one]
    team_two = teamabbr[team_two]

    return team_one, team_two


def convertUserName(userProfile):
    if userProfile not in userabbr:
        return userProfile
    else:
        return userabbr[userProfile]

def sendErrorMail():
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('sqix@draftify.gg', 'wmcbufnchvorgako')
    msg = MIMEText('Error Occured. Check Cloud log')
    msg['Subject'] = 'Error occured on scrimdata'
    s.sendmail("owsqix@gmailcom","sqix@draftify.gg",msg.as_string())
    s.quit()