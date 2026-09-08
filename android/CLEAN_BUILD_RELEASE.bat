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
call gradlew.bat clean :app:assembleRelease
if errorlevel 1 (
  echo.
  echo [ERROR] فشل بناء Release.
  pause
  exit /b 1
)
if not exist Dist mkdir Dist
copy /Y "app\build\outputs\apk\release\app-release-unsigned.apk" "Dist\ALBAZ_Smart_Crescent_Atlas_v2.2.1_RELEASE_UNSIGNED.apk" >nul
echo.
echo [OK] تم إنشاء Release غير موقع داخل Dist.
echo للتوزيع العام يجب توقيعه بمفتاحك الرسمي.
pause
