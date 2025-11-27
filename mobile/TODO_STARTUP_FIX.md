# TODO: Fix Slow/Stuck Startup – Flutter Mobile App Launch Under 2 Seconds

## Steps to Complete

- [ ] Modify main.dart: Remove heavy initializations (Firebase, FCM, API calls) from main() and move to first screen
- [ ] Edit AndroidManifest.xml: Remove or adjust splash screen meta-data for faster native splash
- [ ] Update pubspec.yaml: Add flutter_native_splash dependency
- [ ] Create splash.png placeholder in assets
- [ ] Run flutter pub run flutter_native_splash:create
- [ ] Move all initialization (API, providers, auth check) into the first screen (LoginScreen) with loading indicator
- [ ] Rebuild APK: flutter clean, flutter pub get, flutter build apk --debug
- [ ] Test APK launch time (must be under 2 seconds)

## Progress Tracking
- Started: [Current Date/Time]
- Completed:
