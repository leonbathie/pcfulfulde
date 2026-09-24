@echo off
title Enrichissement du Corpus et Autocompletion Fulfulde
color 0B
cls
echo ============================================================
echo   GESTIONNAIRE DE CORPUS FULFULDE (PULAAR)
echo ============================================================
echo.
echo Ce script analyse vos fichiers textes (placer dans le dossier 'corpus\')
echo ou vos fichiers glisses-deposes pour enrichir l'autocompletion.
echo.
if "%~1"=="" (
    python apprendre_corpus.py
) else (
    echo Analyse du fichier fourni : %1
    python apprendre_corpus.py "%~1"
)
echo.
echo ============================================================
echo Apprentissage termine ! Le clavier beneficie maintenant
echo de ces nouvelles donnees.
echo ============================================================
pause
