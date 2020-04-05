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

- `msec_` (timestamp % 10^6) 000000..999999 (msec)
  NB: L'IHM affiche 15sec @ 60 FPS = 900 trames, le timestamp de trame peut tourner % 1000000 sur 6 digits.
- `Vol__` (Volume d'air) : 000..600 (mL)
- `Deb__` (Débit) : '+'/'-' 00..80 (L/min)
- `Paw__` (Pression ) : '+'/'-' 000..100 (cmH2O)

Specification sprintf:
`DATA msec_:%06d Vol_:%03d Deb_:%+03.1f Paw_:%+03.1f\tCS8:%02X\n`

Exemples:
```
DATA msec_:012300 Vol__:462 Deb__:+051.0 Paw__:+053.0\tCS8:C5\n
DATA msec_:012400 Vol__:464 Deb__:+051.5 Paw__:+053.6\tCS8:C7\n
```

## Données de cycle respiratoire

Envoyé une fois par cycle respiratoire

`RESP`
Suivi de chacun des champs et données suivants :

- `IE___` (Rapport I/E) : 20 .. 60 (20 => 1/2, 22 => 1/2.2, ...)
- `FR___` (Fréquence Respiratoire) : 00..99 (1/min)
- `VTe__` (Volume tidal ou courant expiré) : 000..999 (mL)
- `PCRET` (Pression maximale Pcrete) : 00..99 (cmH2O)
- `VM___` (Volume Minute expiré) : '+'/'-' 00..99 (L/min)
- `PPLAT` (Pression Plateau) : 00..99 (cmH2O)
- `PEP__` (Pression Expiratoire Positive) : 00..99 (cmH2O) NB: moyenne Paw sur dernières 100ms expiration

Specification sprintf:
`RESP IE___:%02d FR___:%02d VTe__:%03d PCRET:%02d VM___:%+02d PPLAT:%02d PEP__:%02d\tCS8:%02X\n`

## Envoi réglages courants

Envoyé après INIT et à chaque modification d'un setting

`SET_` suivi du même champs que contenu dans le message `SET_` acquitté (voir section Réglages).

Exemple:
```
SET_ Vt___:0550\tCS8:1A\n
```

# IHM > Controller

## Réglages

On s'attends a recevoir les réglages (validés par l'IHM) 1 par 1 de manière épisodique avec un identifiant.
Envoyé 1 fois, l'affichage sera mis à jour à réception de la valeur courante du contrôleur

`SET_` suivi d'un réglage parmi :

- `VT___` (Volume tidal ou courant) : 100..600 (mL)
- `FR___` (Fréquence Respiratoire) : 12..35 (1/min)
- `PEP__` (Pression Expiratoire Positive) : 05..20 (cmH2O)
- `FLOW_` (Débit max inspiratoire) : 20..60 (L/min)
- `TPLAT` (Temps Plateau) : 0100..1000 (ms)

ou parmi ces réglages d'alarme

- `PMAX_` (Pression max) : 00.0..99.9 (cmH2O) 
- `PMIN_` (Pression Minimum inspiration) : 00.0..99.9 (cmH2O) 
- `VTMIN` (Volume Minimum inspiration) : 0200..1000 (mL)

Exemple:
```
SET_ Vt___:550\tCS8:1A\n
```

## Pauses

`PINS` (pause inspiratoire débit 0) suivi d'une durée max : 000..999 (msec) NB: charge à l'IHM de réémettre la pause tant qu'on constate le bouton enfoncé, un envoi d'une durée de 0 relance la respiration

`PEXP` (pause inspiratoire débit 0) suivi d'une durée max : 000..999 (msec) NB: charge à l'IHM de réémettre la pause tant qu'on constate le bouton enfoncé, un envoi d'une durée de 0 relance la respiration

Exemple:
```
PINS 500\tCS8:2F\n
PEXP 500\tCS8:4E\n
```

## Pause Bip

Envoyé pour désactiver les bip sonores pendant une durée donnée

`PBIP` suivi d'une durée en ms 000000..999999 (ms)

Exemple:
```
PBIP 000500\tCS8:2F\n
```

## Alarmes

UNIQUEMENT loggé !!! Si possible 1 fois lors de l'activation (nécessite de mémoriser la déactivation)

`ALRM` suivi d'un texte de taille variable ne contenant pas le caractère '\t'.

Textes d'alarmes connues :
- 'Pression insufflation > seuil maximum : valeur reele > seuil'
- 'Pression insufflation < seuil minimum : valeur reele < seuil'
- 'PEP basse : valeur reelle < consigne - 2'
- 'PEP Haute : valeur reelle > consigne + 2'
- 'VTe bas : valeur reele < seuil'
- 'VTe Haut : valeur reele > seuil'
- 'Batterie dégradée, arret imminent'

Specification sprintf: 
`ALRM %s\tCS8:%02X\n`

Exemple:
```
ALRM Activation : Pression insufflation < seuil minimum : 15 < 20\tCS8:D8\n
```
