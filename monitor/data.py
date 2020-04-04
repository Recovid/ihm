class Data:
    TIME="timestamp"
    VT="vt" # volume courant (mL)
    FR="fr" # frequence respiratoire (1/min)
    FRMIN="frmin"
    PEP="pep" # pression expiratoire positive (cmH2O)
    FLOW="flow" # debit max inspiratoire (L/min)
    TPLAT="tplat" # temps plateau (ms)
    IE="I/E"

    PEP_ALARM="pep_alarm"
    VTE="vte"
    VTE_ALARM="vte_alarm"
    VTMIN="vtmin"
    PPLAT="pplat"
    PCRETE="pcrete"
    PCRETE_ALARM="pcrete_alarm"
    PMAX="pmax"
    PMIN="pmin"
    VM="VM"
    VMMIN="vmmin"

class Setting:
    def __init__(self, key, vmin=0, vmax=100, default=0, step=1):
        self.vmin=vmin
        self.vmax=vmax
        self.step=step
        self.default=default
        self.key=key

SETTINGS = {
    # resp. cycle
    Data.VT: Setting(Data.VT,100,600,default=300, step=50),
    Data.FR: Setting(Data.FR,12,35,default=18),
    Data.PEP: Setting(Data.PEP,5,20,default=5),
    Data.FLOW: Setting(Data.FLOW,20,60,default=60, step=2),
    Data.TPLAT: Setting(Data.TPLAT,0.1,1,default=0.1, step=0.1),

    # alarms
    Data.PMIN: Setting(Data.PMIN,0,30,default=15), # TODO confirm default
    Data.PMAX: Setting(Data.PMAX,1,80,default=60), # TODO confirm default
    Data.VTMIN: Setting(Data.VTMIN,100,1000,default=300, step=50), # TODO confirm default
    Data.VMMIN: Setting(Data.VMMIN,100,1000,default=100, step=50), # TODO confirm default
    Data.FRMIN: Setting(Data.FRMIN,12,35,default=12), # TODO confirm default
}
