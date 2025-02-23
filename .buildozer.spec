[app]
title = KivyTest
package.name = kivytest
package.domain = org.test
source.dir = .
source.include_exts = py
# source.include_patterns = assets/*, data/*
version = 0.1
# requirements = python3,kivy==2.2.1,youtube_transcript_api==0.6.2,certifi
# requirements = python3,kivy==2.2.1,kivymd==1.1.1,youtube_transcript_api==0.6.3,certifi,cython==0.29.28,pillow
requirements = python3,kivy==2.2.1,kivymd==1.1.1,youtube_transcript_api==0.6.3,certifi,cython==0.29.28,pillow
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0

# Android specific
android.permissions = INTERNET
android.api = 33

# Android SDK build-tools version
android.build_tools_version = 33.0.0
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True
android.skip_update = False

# (str) python-for-android fork to use, defaults to upstream (kivy)
p4a.branch = master

# (str) python-for-android specific commit to use, defaults to HEAD, must be within p4a.branch
#p4a.commit = HEAD

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port =

[buildozer]
log_level = 2
warn_on_root = 1
