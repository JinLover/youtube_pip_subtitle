[app]
title = YouTube PiP Subtitle
package.name = ytpipsubtitle
package.domain = org.ytpipsubtitle

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1
requirements = python3,kivy,kivymd,youtube_transcript_api,requests,charset_normalizer,urllib3,idna,certifi,defusedxml,plyer

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0

android.permissions = INTERNET,SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE,PACKAGE_USAGE_STATS,GET_TASKS
android.api = 33
android.minapi = 28
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.enable_androidx = True


[buildozer]
log_level = 2
warn_on_root = 1
warn_on_boot_failure = 1
python_executable = /opt/homebrew/anaconda3/envs/ytpip/bin/python
