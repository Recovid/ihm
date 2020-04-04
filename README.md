# Recovid IHM

Vous trouverez ci-dessous de quoi lancer l'interface Recovid sur linux/raspbian (ça vaut mieux qu'un long discours et pas le temps de faire mieux pour l'instant)

On part sur le principe que l'on a un écran tactile pour sélectionner les boutons de paramétrages (en bas) et les boutons (à droite).

Les courbes sont pour l'instant simulées.


# Requirement
  libjpeg-dev
  Python 3
  
  dépendance :
  tkinter
  matplotlib
  pillow

# Install

Sous Linux ou Raspbian (+ écran 800x480 + clavier USB)
```
sudo apt-get install libatlas-base-dev libjpeg-dev
git clone https://github.com/Recovid/ihm.git
cd ihm
python3.7 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
python main.py
```
