@echo off
title SciMath Visual Studio - Installer Setup
color 0b

echo ====================================================================
echo             SCIMATH VISUAL STUDIO INSTALLATION WIZARD                
echo ====================================================================
echo.
echo  This wizard will install SciMath Visual Studio offline application
echo  on your computer. It will create shortcuts on your Desktop and 
echo  Start Menu for easy launch.
echo.
echo ====================================================================
echo.

set "EXE_SOURCE=dist\SciMathStudio.exe"
if not exist "%EXE_SOURCE%" (
    echo [ERROR] SciMathStudio.exe was not found in the dist directory.
    echo Please make sure you have compiled the application first.
    pause
    exit /b
)

set "DEFAULT_PATH=%LOCALAPPDATA%\SciMathStudio"
echo Default installation folder:
echo   %DEFAULT_PATH%
echo.
set /p "USER_CONFIRM=Confirm installation? (Y/N): "
if /i "%USER_CONFIRM%" neq "y" (
    echo.
    echo Installation aborted by user.
    pause
    exit /b
)

echo.
echo Installing SciMath Visual Studio...
echo -------------------------------------------------------------

:: Create install directory
if not exist "%DEFAULT_PATH%" (
    mkdir "%DEFAULT_PATH%"
)

:: Copy executable
echo [1/3] Copying application assets...
copy "%EXE_SOURCE%" "%DEFAULT_PATH%\SciMathStudio.exe" > nul
if %errorlevel% neq 0 (
    echo [ERROR] Failed to print files to target destination. Check permissions.
    pause
    exit /b
)

:: Copy icon
if exist "icon.ico" (
    copy "icon.ico" "%DEFAULT_PATH%\icon.ico" > nul
)

:: Create shortcuts using PowerShell
echo [2/3] Registering system shortcuts...
set "TEMP_PS=%TEMP%\create_shortcuts.ps1"
(
echo $WshShell = New-Object -ComObject WScript.Shell
echo $DesktopPath = [System.Environment]::GetFolderPath^('Desktop'^)
echo $Shortcut = $WshShell.CreateShortcut^("$DesktopPath\SciMath Studio.lnk"^)
echo $Shortcut.TargetPath = "%DEFAULT_PATH%\SciMathStudio.exe"
echo $Shortcut.WorkingDirectory = "%DEFAULT_PATH%"
echo $Shortcut.IconLocation = "%DEFAULT_PATH%\SciMathStudio.exe, 0"
echo $Shortcut.Description = "Interactive Science and Mathematics Visual Studio"
echo $Shortcut.Save^(^)
echo.
echo $StartMenuPath = [System.Environment]::GetFolderPath^('Programs'^)
echo $StartShortcut = $WshShell.CreateShortcut^("$StartMenuPath\SciMath Studio.lnk"^)
echo $StartShortcut.TargetPath = "%DEFAULT_PATH%\SciMathStudio.exe"
echo $StartShortcut.WorkingDirectory = "%DEFAULT_PATH%"
echo $StartShortcut.IconLocation = "%DEFAULT_PATH%\SciMathStudio.exe, 0"
echo $StartShortcut.Save^(^)
) > "%TEMP_PS%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%TEMP_PS%"
del "%TEMP_PS%"

:: Create uninstaller
echo [3/3] Creating uninstall configuration files...
set "UNINSTALLER=%DEFAULT_PATH%\uninstall.bat"
(
echo @echo off
echo title SciMath Visual Studio - Uninstaller
echo color 0c
echo echo ====================================================================
echo echo             SCIMATH VISUAL STUDIO UNINSTALLER WIZARD                
echo echo ====================================================================
echo echo.
echo echo  Are you sure you want to completely uninstall SciMath Studio?
echo echo.
echo set /p "UNCONFIRM=Confirm uninstall? (y/n): "
echo if /i "%%UNCONFIRM%%" neq "y" exit /b
echo.
echo echo Removing shortcuts...
echo set "DesktopLink=%%USERPROFILE%%\Desktop\SciMath Studio.lnk"
echo if exist "%%DesktopLink%%" del "%%DesktopLink%%"
echo set "StartLink=%%USERPROFILE%%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\SciMath Studio.lnk"
echo if exist "%%StartLink%%" del "%%StartLink%%"
echo.
echo echo Cleaning files...
echo timeout /t 2 /nobreak ^> nul
echo del "%%LOCALAPPDATA%%\SciMathStudio\SciMathStudio.exe" 2^>nul
echo del "%%LOCALAPPDATA%%\SciMathStudio\icon.ico" 2^>nul
echo del "%UNINSTALLER%" 2^>nul
echo rmdir "%%LOCALAPPDATA%%\SciMathStudio" 2^>nul
echo.
echo echo Uninstall completed successfully.
echo pause
) > "%UNINSTALLER%"

:: Create Shortcut for uninstaller in Start Menu
set "TEMP_PS=%TEMP%\create_uninstaller_shortcut.ps1"
(
echo $WshShell = New-Object -ComObject WScript.Shell
echo $StartMenuPath = [System.Environment]::GetFolderPath^('Programs'^)
echo $UnShortcut = $WshShell.CreateShortcut^("$StartMenuPath\Uninstall SciMath Studio.lnk"^)
echo $UnShortcut.TargetPath = "%DEFAULT_PATH%\uninstall.bat"
echo $UnShortcut.WorkingDirectory = "%DEFAULT_PATH%"
echo $UnShortcut.Save^(^)
) > "%TEMP_PS%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%TEMP_PS%"
del "%TEMP_PS%"

echo -------------------------------------------------------------
echo.
echo  SUCCESS! SciMath Visual Studio has been successfully installed.
echo.
echo  You can now launch it:
echo    - Clicking the Shortcut on your Desktop (SciMath Studio)
echo    - Searching 'SciMath Studio' in your Windows Start Menu
echo.
echo ====================================================================
pause
exit /b
