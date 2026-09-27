@echo off
title Installation de Fulfulde Keyboard
color 0A
cls
echo ============================================================
echo   INSTALLATION DE FULFULDE KEYBOARD
echo ============================================================
echo.
echo Fulfulde Keyboard va etre ajoute a Windows (Win + Espace : FUL),
echo avec ses suggestions et sa correction automatique.
echo Cliquez sur 'Oui' quand Windows demande une autorisation.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer_clavier_pulaar.ps1"
echo.
pause
