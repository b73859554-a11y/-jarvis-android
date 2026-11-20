[app]
title = JARVIS AI Assistant
package.name = jarvisassistant
package.domain = com.example
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
version = 1.0.0
requirements = python3,kivy,plyer,pyjnius
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,RECORD_AUDIO,CAMERA
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
