@echo off
rem Lance le Clavier Pulaar sans fenetre noire : son icone apparait pres de
rem l'horloge (clic : parametres, clic droit : quitter).
rem Les messages du moteur vont dans %APPDATA%\ClavierPulaar\journal.txt
start "" pythonw "%~dp0clavier_fulfulde_natif.py"
