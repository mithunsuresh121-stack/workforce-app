# Flutter Testing Environment Setup Instructions

## Prerequisites
- Ensure you have Flutter SDK installed on your machine.
- Supported OS: macOS, Windows, Linux.
- Minimum Flutter version: 3.0.0 (check with `flutter --version`).

## Install Flutter SDK
1. Download Flutter SDK from https://flutter.dev/docs/get-started/install
2. Extract the archive to a desired location.
3. Add Flutter to your system PATH:
   - macOS/Linux: Add `export PATH="$PATH:[PATH_TO_FLUTTER]/bin"` to your shell profile.
   - Windows: Add Flutter's `bin` directory to the system environment variables.

## Verify Installation
Run:
```
flutter doctor
```
Fix any issues reported by `flutter doctor`.

## Set Up IDE
- Install Flutter and Dart plugins for your IDE (VSCode, Android Studio).

## Install Dependencies
In your project root (frontend/), run:
```
flutter pub get
```

## Run Widget Tests
To run widget and unit tests, execute:
```
flutter test
```

## Additional Notes
- For integration tests, consider setting up `integration_test` package.
- Ensure device/emulator is configured if running integration tests.
- For CI, configure Flutter environment accordingly.

---

This guide will help you set up the Flutter environment to run automated tests for the NotificationsScreen and other widgets.
