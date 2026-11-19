@echo off
REM Compila el APK de SkonditBeats contra la API de produccion (Vercel).
REM El APK funciona solo, con datos o Wi-Fi, sin la PC ni el cable.
flutter build apk --release --dart-define=API_URL=https://skonditbeats-backend.vercel.app/api || exit /b 1
echo.
echo APK: build\app\outputs\flutter-apk\app-release.apk
echo Instalar en el celular conectado: D:\AndroidSDK\platform-tools\adb.exe install -r build\app\outputs\flutter-apk\app-release.apk
