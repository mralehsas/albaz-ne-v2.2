@echo off
setlocal
cd /d "%~dp0"
if not exist gradlew.bat (
  echo [INFO] Gradle Wrapper غير موجود بعد.
  echo افتح المشروع في Android Studio مرة واحدة او شغل:
  echo gradle wrapper --gradle-version 8.9
  pause
  exit /b 1
)
call gradlew.bat clean :app:assembleDebug
if errorlevel 1 (
  echo.
  echo [ERROR] فشل البناء.
  pause
  exit /b 1
)
if not exist Dist mkdir Dist
copy /Y "app\build\outputs\apk\debug\app-debug.apk" "Dist\ALBAZ_Smart_Crescent_Atlas_v2.2.2_DEBUG.apk" >nul
echo.
echo [OK] Dist\ALBAZ_Smart_Crescent_Atlas_v2.2.2_DEBUG.apk
pause
