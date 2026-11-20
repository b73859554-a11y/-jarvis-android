# JARVIS Android Assistant (Python/Kivy)

This is a starter Android app project. It can be built into a debug APK using GitHub Actions, from a phone browser.

## Included
- Kivy Android UI
- Android speech-recognition prompt (uses Android's installed speech recognition service)
- Text-to-speech via Plyer
- Launch shortcuts for common apps
- Time response
- Flashlight attempt using Android CameraManager
- Optional AI API code (API key is deliberately blank)

## Important limitations
- This is a starter prototype, not a complete Iron Man assistant.
- It does NOT implement an always-on wake word.
- It does NOT keep listening while the phone is locked.
- Android restricts background microphone use. A persistent foreground service and user-visible notification, plus appropriate Android service code and permissions, are needed for any lock-screen listening design. Android may still stop it.
- Accessibility, notification access, device-admin screen lock, calls, and message sending need separate user-granted permissions and careful native implementation. This project does not bypass the lock screen or silently send messages.
- The flashlight implementation may need camera selection refinement on some Samsung models.
- The optional AI key must not be hard-coded into a public APK. Use a private backend for a real release.

## Build APK using only your phone
1. Create a GitHub account if needed.
2. Create a new repository named `jarvis-android`.
3. Upload all files and folders from this project to the repository (including `.github/workflows/build-apk.yml`).
4. Open the repository's **Actions** tab.
5. Select **Build JARVIS APK** and tap **Run workflow** (or push a commit).
6. Wait for the workflow to finish successfully.
7. Open that workflow run and download the `jarvis-debug-apk` artifact.
8. Extract the ZIP on your Samsung phone and install the APK.
9. If Android blocks installation, allow your browser or file manager to install unknown apps for this installation.

## Local build (computer/Linux)
Install Buildozer and run:
    buildozer android debug

## Termux note
A full Buildozer Android toolchain build directly inside ordinary Termux is not the supported path. GitHub Actions is the phone-only build route in this project.
