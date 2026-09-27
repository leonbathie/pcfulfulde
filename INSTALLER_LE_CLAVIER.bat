@echo off
title Installation du Clavier Pulaar (Fulfulde)
color 0A
cls
echo ============================================================
echo   INSTALLATION DU CLAVIER PULAAR (FULFULDE)
echo ============================================================
echo.
echo Le clavier Pulaar va etre installe : lettres pulaar avec votre
echo clavier habituel, suggestions et correction automatique.
echo Cliquez sur 'Oui' quand Windows demande une autorisation.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer_clavier_pulaar.ps1"
echo.
pause
