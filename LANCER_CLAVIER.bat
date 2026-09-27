@echo off
rem Lance Fulfulde Keyboard sans fenetre noire : son icone apparait pres de
rem l'horloge (clic : parametres, clic droit : quitter).
rem Les messages du moteur vont dans %APPDATA%\FulfuldeKeyboard\journal.txt
start "" pythonw "%~dp0clavier_fulfulde_natif.py"
