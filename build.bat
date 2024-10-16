@echo off

:: Install Google Chrome
echo Installing Google Chrome...
start /wait chrome_installer.exe

:: You will need to download the Google Chrome installer manually or automate the download in some way
:: The above command assumes you have the installer saved as chrome_installer.exe in the same directory

:: Install ChromeDriver
echo Installing ChromeDriver...
REM Get the Chrome version from the installed Google Chrome
for /f "tokens=3" %%a in ('reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome" /v Version') do set CHROME_VERSION=%%a
echo Chrome Version: %CHROME_VERSION%

REM Download ChromeDriver
set CHROMEDRIVER_URL=https://chromedriver.storage.googleapis.com/%CHROME_VERSION%/chromedriver_win32.zip
curl -O %CHROMEDRIVER_URL%
echo Downloading ChromeDriver...

REM Unzip the downloaded ChromeDriver zip file
powershell -command "Expand-Archive -Path chromedriver_win32.zip -DestinationPath ."

REM Move ChromeDriver to a suitable location (e.g., C:\Windows\System32)
move chromedriver.exe C:\Windows\System32\

:: Make ChromeDriver executable (not strictly necessary on Windows, but for consistency)
echo Granting execute permissions to ChromeDriver...
icacls C:\Windows\System32\chromedriver.exe /grant Everyone:(R,X)

:: Install Python dependencies (if using pip)
echo Installing Python dependencies...
pip install -r requirements.txt

echo Build script completed successfully.
