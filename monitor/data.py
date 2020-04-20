class Data:
    MAXPAW="max_paw_between_RespMsg"
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
    VTMAX="vtmax"
    PPLAT="pplat"
    PCRETE="pcrete"
    PCRETE_ALARM="pcrete_alarm"
    PMAX="pmax"
    PMIN="pmin"
    VM="VMe"
    VMMIN="vmmin"

class Setting:
    def __init__(self, key, vmin=0, vmax=100, default=0, step=1, bigStep=1):
        self.vmin=vmin
        self.vmax=vmax
        self.step=step
        self.bigStep=bigStep
        self.default=default
        self.key=key

SETTINGS = {
    # resp. cycle
    Data.VT: Setting(Data.VT,100,600,default=300, step=10, bigStep=50),
    Data.FR: Setting(Data.FR,12,35,default=18, bigStep=5),
    Data.PEP: Setting(Data.PEP,5,20,default=5, bigStep=2),
    Data.FLOW: Setting(Data.FLOW,20,60,default=60, step=2, bigStep=5),
    Data.IE: Setting(Data.IE, 2, 6, default=2, step=0.1, bigStep=0.2),

    # alarms
    Data.PMAX: Setting(Data.PMAX,12,90,default=60, step=1),
    Data.PMIN: Setting(Data.PMIN,2,60,default=20, step=1),
    Data.VTMIN: Setting(Data.VTMIN,100,1000,default=150, step=50),
    Data.VTMAX: Setting(Data.VTMAX,100,1000,default=1000, step=50),
    Data.VMMIN: Setting(Data.VMMIN,2,30,default=3, step=1),
}
