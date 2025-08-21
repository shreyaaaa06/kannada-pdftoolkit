@echo off
echo Cleaning up temporary files...

REM Clean uploads folder
if exist "uploads" (
    echo Cleaning uploads folder...
    del /q /s uploads\* 2>nul
)

REM Clean output folder
if exist "output" (
    echo Cleaning output folder...
    del /q /s output\* 2>nul
)

REM Clean static uploads folder
if exist "static\uploads" (
    echo Cleaning static uploads folder...
    del /q /s static\uploads\* 2>nul
)

REM Clean Python cache
if exist "__pycache__" (
    echo Cleaning Python cache...
    rmdir /s /q __pycache__ 2>nul
)

if exist "utils\__pycache__" (
    rmdir /s /q utils\__pycache__ 2>nul
)

echo Cleanup completed!
pause
