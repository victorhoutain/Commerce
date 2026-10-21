@echo off
setlocal
cd /d "%~dp0"
title Petit Nid - lancement et diagnostic
echo.
echo =============================================
echo            PETIT NID - WINDOWS
echo =============================================
echo.
if not exist "%~dp0Petit_Nid.exe" (
 echo ERREUR : Petit_Nid.exe est introuvable dans ce dossier.
 echo Decompresse tout le ZIP dans un dossier avant de lancer ce fichier.
 pause
 exit /b 2
)
set "LOG=%TEMP%\Petit_Nid_Diagnostic.log"
if exist "%LOG%" del /q "%LOG%" >nul 2>&1
echo Demarrage de Petit Nid. Une fenetre du jeu doit apparaitre.
echo Fichier de diagnostic : %LOG%
echo.
start "" /wait "%~dp0Petit_Nid.exe" --rendering-driver opengl3 --verbose --log-file "%LOG%"
set "CODE=%ERRORLEVEL%"
echo.
echo Le jeu est ferme. Code de sortie : %CODE%
if exist "%LOG%" (
 echo.
 echo ------- Journal Godot -------
 type "%LOG%"
 echo ------- Fin du journal -------
) else (
 echo Aucun journal cree. Windows a peut-etre bloque le programme.
)
echo.
echo Si le jeu ne s'est jamais affiche, copie le texte affiche
echo dans cette fenetre et envoie-le dans notre discussion.
echo.
pause
exit /b %CODE%
