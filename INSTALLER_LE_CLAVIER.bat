@echo off
title Installation du Clavier Pulaar (Fulfulde)
color 0A
cls
echo ============================================================
echo   INSTALLATION DU CLAVIER PULAAR (FULFULDE)
echo ============================================================
echo.
echo Le clavier Pulaar va etre ajoute a Windows (Win + Espace),
echo avec ses suggestions et sa correction automatique.
echo Cliquez sur 'Oui' quand Windows demande une autorisation.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer_clavier_pulaar.ps1"
echo.
pause
