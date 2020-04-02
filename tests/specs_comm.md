Spécification des trames de communication basées sur le CdC :
https://github.com/Recovid/Documentation/wiki/01-Cahier-des-charges

# Communication

Canal de communication : port série sur USB.
Un débit type teensy pour Serial sur USB est de 12MBit/s soit 50Ko @ 30FPS ( d'après https://www.pjrc.com/teensy/td_serial.html )

# Structure générale

Un format texte (ASCII) pour faciliter la mise au point en considérant qu'on aura pas besoin de compacifier les trames. Pour plus de sûreté et pour simplifier la mise au point, on choisi :
- des trames de taille variable dont le dernier champ est un checksum (voir ci dessous) préfixé de `\t` et suivi de `\n` (newline)
- des champs séparés par ` ` (espace)
- des données précédées d'un label sur 5 caractères qui identifie la donnée, son étendue (fixe) en nb de caractères et son unité

## Contrôle de redondance cyclique

*Tous* les messages se terminent par
- le séparateur `\t`
- la chaine "CS8:"
- le CRC dont la valeur est la somme de chaque octet précédant cette valeur (dont la chaine "\tCS8:") modulo 256 et exprimé sur 2 caractères hexa : 00..FF.
- le caractère de fin de ligne `\n`

Specification printf de la fin d'un message : `\tCS8:%02X\n`

# Controller > IHM

## Initialisation

Envoyé à la fin de l'initialisation du contrôleur.

`INIT` suivit d'un texte de taille variable ne contenant pas le caractère `\t`.

Specification sprintf: 
`INIT %s\0\tCS8:%02X\n`

## Données mesurées

On s'attend à recevoir @ 25 FPS les dernières valeurs de chaque variable calculée par le contrôleur.

`DATA`
Suivi de chacun des champs et données suivants :

- `msec_` (timestamp % 10^5) 00000..99999 (msec)
  NB: L'IHM affiche 15sec @ 60 FPS = 900 trames, le timestamp de trame peut tourner % 100000 sur 5 digits.
- `Vol__` (Volume d'air) : 0000..1000 (mL)
- `Deb__` (Débit) : '+'/'-' 000..200. (L/min)
- `Paw__` (Pression ) : '+'/'-' 000..100.0 (cmH2O)

Specification sprintf:
`DATA msec_:%05d Vol_:%03d Deb_:%+03.1f Paw_:%+03.1f\tCS8:%02X\n`

Exemples:
```
DATA msec_:12300 Vol__:462 Deb__:+051.0 Paw__:+053.0\tCS8:C5\n
DATA msec_:12400 Vol__:464 Deb__:+051.5 Paw__:+053.6\tCS8:C7\n
```

## Données de cycle respiratoire

Envoyé une fois par cycle respiratoire

`RESP`
Suivi de chacun des champs et données suivants :

- `Fi02_` (Fraction inspirée en di-Oxygène) : 021..100 (%)
- `Vt___` (Volume tidal ou courant) : 0300..800 (mL)
- `FR___` (Fréquence Respiratoire) : 10..35 (1/min)
- `PEP__` (Pression Expiratoire Positive) : 00..15 (cmH2O) NB: différent du réglage ???
- `PIP__` (Pression Inspiratoire de Pointe) : 00.0..99.9 (cmH2O) 
- `PPLAT` (Pression Plateau) : 00.0..99.9 (cmH2O) 

Specification sprintf:
`RESP Fi02_:%03d Vt___:%04d FR___:%02d PEP__:%02.1f PIP__:%02.1f PPLAT:%02.1f\tCS8:%02X\n`

## Alarmes

Envoyé toute les x ms (100ms?) jusqu'à acknowledge

`ALRM` suivi d'un texte de taille variable ne contenant pas le caractère '\t'.

Textes d'alarmes connues :
- 'Pression insufflation > seuil maximum : valeur reele > seuil'
- 'Pression insufflation < seuil minimum : valeur reele < seuil''
- 'PEP basse : valeur reele < seuil'
- 'PEP Haute : valeur reele > seuil''
- 'VTe bas : valeur reele < seuil'
- 'VTe Haut : valeur reele > seuil''
- 'Niveau batterie bas : niveau < seuil'

le changement doit permetre de cree un fichier de log des alarmes.

Specification sprintf: 
`ALRM %s\0\t : %d %s %dCS8:%02X\n`

Exemple:
```
ALRM Pression insufflation < seuil minimum\0\tCS8:D8\n
```

## Acknowledge Setting

Envoyé à chaque reception d'un setting

`RSET` suivi du même champs que contenu dans le message `SET_` acquitté (voir section Réglages).

Exemple:
```
RSET Vt___:0550\tCS8:1A\n
```

# IHM > Controller

## Réglages

On s'attends a recevoir les réglages (validés par l'IHM) 1 par 1 de manière épisodique avec un identifiant.
envoye toute les xms (100ms?) jusqu'a acknowledge

`SET_` suivi d'un réglage parmi :

- `Fi02_` (Fraction inspirée en di-Oxygène) : 021..100 (%)
- `Vt___` (Volume tidal ou courant) : 0300..1000 (mL)
- `PEP__` (Pression Expiratoire Positive) : 00..50 (cmH2O)
- `FR___` (Fréquence Respiratoire) : 12..35 (1/min)
- `PIF__` (Débit de pointe) : 30..90 (1/min)
- `TPLAT` (Temps Plateau) : 000..200 (ms)

ou parmi ces réglages d'alarme

- `PMAX_` (Pression max) : 00.0..99.9 (cmH2O) 
- `PMIN_` (Pression Minimum inspiration) : 00.0..99.9 (cmH2O) 
- `VTMIN` (Volume Minimum inspiration) : 0200..1000 (mL)

Exemple:
```
SET_ Vt___:0550\tCS8:1A\n
```

## Pauses

`PINS` (pause inspiratoire débit 0) suivi d'une durée max : 00..99 (sec) NB: charge à l'IHM de réémettre la pause tant qu'on constate le bouton enfoncé, un envoi d'une durée de 0 relance la respiration

`PEXP` (pause inspiratoire débit 0) suivi d'une durée max : 00..99 (sec) NB: charge à l'IHM de réémettre la pause tant qu'on constate le bouton enfoncé, un envoi d'une durée de 0 relance la respiration

Exemple:
```
PINS 10\tCS8:2F\n
PEXP 02\tCS8:4E\n
```

## Acknowledge Alarmes

Envoyé à chaque reception d'un message d'alarme

`RALM` suivi du même texte que contenu dans le message `ARLM` acquitté (voir section Alarmes).

Specification sprintf :
`RALM %s\tCS8:%02X\n`

Exemple:
```
RALM Pression insufflation < seuil minimum\tCS8:D8\n
```

## Bip sonore

Envoyé pour déclencher un bip sonore d'une durée donnée

`BEEP` suivi d'un seul champ :

- `dur__` (Durée du bip) : 00000..99999 (ms)

Specification sprintf :
`BEEP dur__:%05d\tCS8:%02X\n`

Exemple:
```
BEEP dur__:00500\tCS8:FF\n
```
