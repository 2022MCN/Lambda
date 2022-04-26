import re

class MatchInfo: #Information about current match (map, type, map section, team info)
    def __init__(self):
        self.Map = ''
        self.MapType = ''
        self.RoundName = ''
        self.Section = '-1'
        self.Round = ''
        self.Team_1 = ''
        self.Team_2 = ''
        self.Offense = ''
        self.Defense = ''
        self.Version = ''

class PlayerData: #Player stat on csv
    def __init__(self):
        self.Version = ''
        self.Map = ''
        self.Section = ''
        self.Point = '0'
        self.RoundName = ''
        self.Timestamp = ''
        self.Team = ''
        self.Player = ''
        self.Hero = ''
        self.HeroDamageDealt = '0'
        self.BarrierDamageDealt = '0'
        self.DamageBlocked = '0'
        self.DamageTaken = '0'
        self.Deaths = '0'
        self.Eliminations = '0'
        self.FinalBlows = '0'
        self.EnvironmentalDeaths = '0'
        self.EnvironmentalKills = '0'
        self.HealingDealt = '0'
        self.ObjectiveKills = '0'
        self.SoloKills = '0'
        self.UltimatesEarned = '0'
        self.UltimatesUsed = '0'
        self.HealingReceived = '0'
        self.UltimateCharge = '0'
        self.Cooldown1 = '0'
        self.Cooldown2 = '0'
        self.CooldownSecondaryFire = '0'
        self.CooldownCrouching = '0'
        self.IsAlive = 'True'
        self.TimeElapsed = '0'
        self.Position = ''
        self.MaxHealth = '0'
        self.DeathByHero = ''
        self.DeathByAbility = ''
        self.DeathByPlayer = ''
        self.Resurrected = ''
        self.DuplicatedHero = ''
        self.DuplicateStatus = ''
        self.Health = ''
        self.DefensiveAssists = '0'
        self.OffensiveAssists = '0'
        self.IsBurning = '0'
        self.IsKnockedDown = '0'
        self.IsAsleep = '0'
        self.IsFrozen = '0'
        self.IsUnkillable = '0'
        self.IsInvincible = '0'
        self.IsRooted = '0'
        self.IsStunned = '0'
        self.IsHacked = '0'
        self.FacingDirection = '(0, 0, 0)'
        self.Team1Player1InViewAngle = '0'
        self.Team1Player2InViewAngle = '0'
        self.Team1Player3InViewAngle = '0'
        self.Team1Player4InViewAngle = '0'
        self.Team1Player5InViewAngle = '0'
        self.Team2Player1InViewAngle = '0'
        self.Team2Player2InViewAngle = '0'
        self.Team2Player3InViewAngle = '0'
        self.Team2Player4InViewAngle = '0'
        self.Team2Player5InViewAngle = '0'

class LogPattern: # Regex log patterns
    def __init__(self):
        self.pattern_dupstart = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(DuplicatingStart),(\w*),(\w*)')
        self.pattern_dupend = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(DuplicatingEnd),(\w*)')
        self.pattern_resurrect = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(Resurrected),(\w*)')
        self.pattern_finalblows = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(FinalBlow),(\w*),(\w*),(\w*\s*\w*)')
        self.pattern_suicide = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(Suicide),(\w*)')
        self.pattern_matchInfo = re.compile('(\[(.*?)\])\s(\w*\s*\w*\s*\w*|Watchpoint: Gibraltar|King\'s Row),(\w*\s*\w*),(\w*\s*\w*),(\d)')#,([+-]?([0-9]*[.])?[0-9]+)') # Added Float number for version
        self.pattern_playerInfo = re.compile('(\[(.*?)\])\s(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76)')#,(\w*|Soldier: 76),(\w*|Soldier: 76)') for OW1
        self.pattern_typeControl = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+)')
        self.pattern_typeOthers = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(True|False),(\d*\.?\d+)')
        self.pattern_playerData = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(\w*\s*\w*|Soldier: 76|D.Va),(\w*\s*\w*|Soldier: 76|D.Va),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\W[-]?(\d*\.?\d+), [-]?(\d*\.?\d+), [-]?(\d*\.?\d+)\W),(\w*\s*\w*),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+)')#,//(\W[-]?(\d*\.?\d+), [-]?(\d*\.?\d+), [-]?(\d*\.?\d+)\W),(True|False),(True|False),(True|False),(True|False),(True|False),(True|False),(True|False),(True|False),(True|False),(True|False)')
