
# -*- coding: utf-8 -*-

from enum import IntEnum, Enum

class AlarmType(IntEnum):
    #Alarm define from file Recovid_Userneeds v0.1 13h35
    NONE = 0
    PRESSION_MAX = 1
    PRESSION_MIN = 2
    VOLUME_COURANT = 3
    FREQUENCE_RESPIRATOIRE = 4
    VOLUME_MINUTE = 5
    PEP_MAX = 6
    PEP_MIN = 7
    LOW_BATTERY = 8
    FAILSAFE = 9

    #41 char max
    def GetMessage(self, alarmtype):
        switcher = {
            AlarmType.NONE: "",
            AlarmType.PRESSION_MAX: "DEPASSEMENT SEUIL D\'INSUFFLATION MAX",
            AlarmType.PRESSION_MIN: "PASSAGE SOUS LE SEUIL D\'INSUFFLATION MIN",
            AlarmType.VOLUME_COURANT: "VTe SOUS LE SEUIL",
            AlarmType.FREQUENCE_RESPIRATOIRE: "FREQUENCE RESPIRATOIRE SOUS LE SEUIL",
            AlarmType.VOLUME_MINUTE: "VOLUME MINUTE SOUS LE SEUIL",
            AlarmType.PEP_MAX: "PEP SUPERIEUR A LA NORME",
            AlarmType.PEP_MIN: "PEP INFERIEUR A LA NORME",
            AlarmType.LOW_BATTERY: "BATTERIE DECHARGEE",
            AlarmType.FAILSAFE: "FAILSAFE"
        }
        return switcher.get(alarmtype, "")


    #note Boris: See if we need this or if the info will be given by the controller
    def isHighLevel(self, alarmtype):
        switcher = {
            AlarmType.NONE: False,
            AlarmType.PRESSION_MAX: True,
            AlarmType.PRESSION_MIN: True,
            AlarmType.VOLUME_COURANT: False,
            AlarmType.FREQUENCE_RESPIRATOIRE: False,
            AlarmType.VOLUME_MINUTE: False,
            AlarmType.PEP_MAX: True,
            AlarmType.PEP_MIN: False,
            AlarmType.LOW_BATTERY: True,
            AlarmType.FAILSAFE: False                   #to confirm when specified
        }
        if(switcher.get(alarmtype, False)):
            return AlarmLevel.HIGH_PRIORITY
        else:
            return AlarmLevel.MEDIUM_PRIORITY
        

#number and means of State to clarify
class AlarmState(Enum):
    INACTIVE = 0
    ACTIVE = 1

class AlarmLevel(Enum):
    HIGH_PRIORITY = 0
    MEDIUM_PRIORITY = 1

class Alarm:
    def __init__(self, type, level):
        self.type = type
        self.state = AlarmState.ACTIVE
        self.level = level

    def GetState(self):
        return self.state

    def GetType(self):
        return self.type
    
    def ChangeState(self, newState):
        self.state = newState

    def GetLevel(self):
        return self.level


class AlarmManager:
    def __init__(self):
        self.listActivAlarms = []
        self.highPriorityNb = 0
        self.mediumPriorityNb = 0
        #current alarms mean the Alarm Which is display on the screen : the first of the list

    def GetActivAlarmNb(self):
        return len(self.listActivAlarms)

    def ActivateAlarm(self, Alarm):
        #if there is already an alarm of this type in the list: do not add a new one
        for i in range(len(self.listActivAlarms)):
            if(self.listActivAlarms[i].GetType() == Alarm.GetType() ):
                return

        #To Have always new High Priority (HP) alarm in the top of the list we add HP new Alarm in head of the list and MediumPriority (MP)
        #on the back of the list. Moreover with this method we have always the newest HP alarm display
        if( Alarm.GetLevel() == AlarmLevel.MEDIUM_PRIORITY):
            self.listActivAlarms.insert(self.highPriorityNb, Alarm)
            self.mediumPriorityNb += 1

        elif( Alarm.GetLevel() == AlarmLevel.HIGH_PRIORITY):
            self.listActivAlarms.insert(0, Alarm)
            self.highPriorityNb += 1

    def DeActivateCurrentAlarm(self):
        #delete the alarm of the list
        if( self.GetActivAlarmNb() == 0):
            return
        if(self.GetCurrentMessageLevel() == AlarmLevel.HIGH_PRIORITY):
            self.highPriorityNb -= 1
        elif(self.GetCurrentMessageLevel() == AlarmLevel.MEDIUM_PRIORITY):
            self.mediumPriorityNb -= 1
        del self.listActivAlarms[0]

    def ChangeCurrentAlarmState(self, newStatus ):
        self.listActivAlarms[0].ChangeState(newStatus)

    def GetCurrentMessageState(self):
        #return current message Status
        return self.listActivAlarms[0].GetState()


    def GetCurrentMessageToDisplay(self):
        #should return the associate message
        type = self.listActivAlarms[0].GetType()
        return type.GetMessage(type)

    def GetCurrentMessageLevel(self):
        #return the level of the current alarm
        return self.listActivAlarms[0].GetLevel()
