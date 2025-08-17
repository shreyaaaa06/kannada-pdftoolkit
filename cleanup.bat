@echo off
echo Cleaning up Kannada PDF Toolkit...

REM Test and sample files
echo Deleting test files...
if exist test_*.py del /f /q test_*.py
if exist *_test.py del /f /q *_test.py
if exist test*.pdf del /f /q test*.pdf
if exist sample*.pdf del /f /q sample*.pdf
if exist example*.pdf del /f /q example*.pdf

REM Temporary files
echo Deleting temporary files...
if exist *.tmp del /f /q *.tmp
if exist *.log del /f /q *.log
if exist *.cache del /f /q *.cache
if exist .DS_Store del /f /q .DS_Store
if exist Thumbs.db del /f /q Thumbs.db

REM Python cache files
echo Deleting Python cache...
if exist __pycache__ rmdir /s /q __pycache__
if exist *.pyc del /f /q *.pyc
if exist *.pyo del /f /q *.pyo
if exist *.pyd del /f /q *.pyd

REM IDE files
echo Deleting IDE files...
if exist .vscode rmdir /s /q .vscode
if exist .idea rmdir /s /q .idea

REM Backup files
echo Deleting backup files...
if exist *.bak del /f /q *.bak
if exist *.backup del /f /q *.backup
if exist *_backup.* del /f /q *_backup.*
if exist *_old.* del /f /q *_old.*
if exist *.orig del /f /q *.orig

REM Build artifacts
echo Deleting build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info
if exist MANIFEST del /f /q MANIFEST

REM Draft documentation
echo Deleting draft docs...
if exist README_draft.md del /f /q README_draft.md
if exist NOTES.md del /f /q NOTES.md
if exist TODO.md del /f /q TODO.md
if exist CHANGELOG_draft.md del /f /q CHANGELOG_draft.md

echo Cleanup completed!
pause
