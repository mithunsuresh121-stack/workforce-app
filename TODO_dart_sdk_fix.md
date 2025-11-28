# TODO: Fix Dart SDK Version Mismatch in CI

## Steps to Complete
- [x] Update Flutter version in `.github/workflows/build-apk.yml` from '3.3.0' to '3.19.0' to ensure Dart SDK >=3.3.0 compatibility.
 - [x] Commit and push the changes to the repository to trigger a new CI workflow run.
 - [ ] Verify that the CI build succeeds by checking the workflow logs for successful `flutter pub get` and APK build.
- [ ] Locally upgrade Flutter (run `flutter upgrade` or `flutter version 3.19.0`) and test `flutter pub get` in the `./mobile` directory to confirm no dependency errors.
- [ ] Review and update other workflows (e.g., `mobile-tests.yml`) if they use an outdated Flutter version, applying the same fix.
