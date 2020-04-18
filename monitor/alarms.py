
# -*- coding: utf-8 -*-

from enum import IntEnum, Enum

class AlarmType(IntEnum):
    #Alarm define from file Recovid_Userneeds v0.1 13h35
    NONE = 0
    PRESSION_MAX = 1
    PRESSION_MIN = 2
    VOLUME_COURANT = 3
    VOLUME_MINUTE = 4
#    FREQUENCE_RESPIRATOIRE = 4
    PEP_MAX = 6
    PEP_MIN = 7
    BATTERY_A = 8
    BATTERY_B = 9
    BATTERY_C = 10
    BATTERY_D = 11
    LOST_CPU = 12
    CAPT_PRESS = 13
    IO_MUTE = 14

    def GetAssociateCode(alarmtype):
        switcher = {
            AlarmType.NONE: "",
            AlarmType.PRESSION_MAX: "PMAX",
            AlarmType.PRESSION_MIN: "PMIN",
            AlarmType.VOLUME_COURANT: "VT_MIN",
            AlarmType.VOLUME_MINUTE: "VM_MIN",
            AlarmType.PEP_MAX: "PEP_MAX",
            AlarmType.PEP_MIN: "PEP_MIN",
            AlarmType.BATTERY_A: "BATT_A",
            AlarmType.BATTERY_B: "BATT_B",
            AlarmType.BATTERY_C: "BATT_C",
            AlarmType.BATTERY_D: "BATT_D",
            AlarmType.LOST_CPU: "CPU_LOST",
            AlarmType.CAPT_PRESS: "P_KO",
            AlarmType.IO_MUTE: "IO_MUTE",
        }
        return switcher.get(alarmtype, "")

    #41 char max
    def GetMessage(self, alarmtype):
        switcher = {
            AlarmType.NONE: "",
            AlarmType.PRESSION_MAX: "Pression voies aérien. > seuil (Pmax)",
            AlarmType.PRESSION_MIN: "Pression voies aérien. < seuil (Pmin)",
            AlarmType.VOLUME_COURANT: "Volume Tidal expiré < seuil (VTmin)",
            AlarmType.VOLUME_MINUTE: "Volume Minute expiré < seuil (VMmin)",
            AlarmType.PEP_MAX: "PEP > consigne+2 cmH2O (PEPmax)",
            AlarmType.PEP_MIN: "PEP < consigne-2 cmH20 (PEPmin)",
            AlarmType.BATTERY_A: "Sur batterie depuis 1 à 15 min",                              #message battery A
            AlarmType.BATTERY_B: "Sur batterie depuis plus de 25 min",                          #message battery D
            AlarmType.BATTERY_C: "Sur batterie depuis 15 à 20 min",                             #message battery B
            AlarmType.BATTERY_D: "Sur batterie depuis 20 à 25 min",                             #message battery C
            AlarmType.LOST_CPU: "Erreur critique, arrêt immédiat (failure)",
            AlarmType.CAPT_PRESS: "Pression mesurée incohérente",
            AlarmType.IO_MUTE: "Re-Basculer interrupteur sur I",
        }
        return switcher.get(alarmtype, "")


    #note Boris: See if we need this or if the info will be given by the controller
    def isHighLevel(self, alarmtype):
        switcher = {
            AlarmType.NONE: 2,
            AlarmType.PRESSION_MAX: 0,
            AlarmType.PRESSION_MIN: 0,
            AlarmType.VOLUME_COURANT: 1,
            AlarmType.VOLUME_MINUTE: 1,
            AlarmType.PEP_MAX: 0,
            AlarmType.PEP_MIN: 0,
            AlarmType.BATTERY_A: 2,
            AlarmType.BATTERY_B: 0,
            AlarmType.BATTERY_C: 1,
            AlarmType.BATTERY_D: 1,
            AlarmType.LOST_CPU: 0,
            AlarmType.CAPT_PRESS: 0,
            AlarmType.IO_MUTE: 2,
        }
        if(switcher.get(alarmtype, 0) == 0):
            return AlarmLevel.HIGH_PRIORITY
        elif(switcher.get(alarmtype, 0) == 1):
            return AlarmLevel.MEDIUM_PRIORITY
        else:
            return AlarmLevel.LOW_PRIORITY
        

#number and means of State to clarify
class AlarmState(Enum):
    INACTIVE = 0
    ACTIVE = 1

class AlarmLevel(Enum):
    HIGH_PRIORITY = 0
    MEDIUM_PRIORITY = 1
    LOW_PRIORITY = 2

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
        self.listHighAlarms = []
        self.listMedAlarms = []
        self.listLowAlarms = []

    def GetActivAlarmNb(self):
        return len(self.listHighAlarms) + len(self.listMedAlarms) + len(self.listLowAlarms)

    def ActivateAlarm(self, Alarm):

        currentType = Alarm.GetType()
        if( currentType == AlarmLevel.HIGH_PRIORITY):

            for i in range(len(self.listHighAlarms)):
                if(self.listHighAlarms[i].GetType() == currentType ):
                    return
            self.listHighAlarms.insert(0, Alarm)


        elif( currentType == AlarmLevel.MEDIUM_PRIORITY):
            for i in range(len(self.listMedAlarms)):
                if(self.listMedAlarms[i].GetType() == currentType ):
                    return
            self.listMedAlarms.insert(0, Alarm)

        else:
            for i in range(len(self.listLowAlarms)):
                if(self.listLowAlarms[i].GetType() == currentType ):
                    return
            self.listLowAlarms.insert(0, Alarm)

    def DeActivateCurrentAlarm(self):
        #delete the alarm of the list
        if( len(self.listHighAlarms) != 0):
            del self.listHighAlarms[0]

        elif( len(self.listMedAlarms) != 0):
            del self.listMedAlarms[0]

        elif( len(self.listLowAlarms) != 0):
            del self.listLowAlarms[0]

    def DeActivateAlarm(self, alarmtype):
        #delete alarm of the given type
        indice = 0
        found = False
        for i in range(len(self.listHighAlarms)):
            if(self.listHighAlarms[i].GetType() == alarmtype):
                indice = i
                found = True
                break
        if( found ):
            self.listHighAlarms.pop(indice)
            return

        for i in range(len(self.listMedAlarms)):
            if(self.listMedAlarms[i].GetType() == alarmtype):
                indice = i
                found = True
                break
        if( found ):
            self.listMedAlarms.pop(indice)
            return

        for i in range(len(self.listLowAlarms)):
            if(self.listLowAlarms[i].GetType() == alarmtype):
                indice = i
                found = True
                break
        if( found ):
            self.listLowAlarms.pop(indice)
            return

    def GetCurrentMessageState(self):
        #return current message Status
        if( len(self.listHighAlarms) != 0):
            return self.listHighAlarms[0].GetState()
        elif( len(self.listMedAlarms) != 0):
            return self.listMedAlarms[0].GetState()
        elif( len(self.listLowAlarms) != 0):
            return self.listLowAlarms[0].GetState()
        
        return ''


    def GetCurrentMessageToDisplay(self):
        #should return the associate message
        type = AlarmType.NONE
        if( len(self.listHighAlarms) != 0):
            type = self.listHighAlarms[0].GetType()
        elif( len(self.listMedAlarms) != 0):
            type = self.listMedAlarms[0].GetType()
        elif( len(self.listLowAlarms) != 0):
            type = self.listLowAlarms[0].GetType()
        return type.GetMessage(type)

    def GetCurrentMessageLevel(self):
        #return the level of the current alarm
        if( len(self.listHighAlarms) != 0):
            return self.listHighAlarms[0].GetLevel()
        elif( len(self.listMedAlarms) != 0):
            return self.listMedAlarms[0].GetLevel()
        elif( len(self.listLowAlarms) != 0):
            return self.listLowAlarms[0].GetLevel()
        
        return AlarmLevel.LOW_PRIORITY
