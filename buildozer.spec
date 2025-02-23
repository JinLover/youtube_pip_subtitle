[app]

# (str) Title of your application
title = YouTube PiP Subtitle

# (str) Package name
package.name = youtubepipsubtitle

# (str) Package domain (needed for android/ios packaging)
package.domain = org.jinlover

# (str) Source code where the main.py live
source.dir = ./compile

# (str) Main source file
# source.filename = test_code/test.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,ttc,kv

# (list) Source files to exclude (let empty to not excluding anything)
#source.exclude_exts = spec

# (list) List of inclusions using pattern matching
source.include_patterns = main.py,*.ttc,*.kv

# (str) Application versioning (method 1)
# version.regex = __version__ = '(.*)'
# version.filename = %(source.dir)s/main.py

# (str) Application versioning (method 2)
version = 0.1

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Application requirements
requirements = python3==3.11.0,
    kivy==2.2.1,
    pyjnius==1.6.1,
    android,
    youtube_transcript_api==0.6.1,
    plyer==2.1.0

# (list) Garden requirements
# garden_requirements =

# (list) Python modules you want to be removed from the app before packaging
# This can be useful to avoid including unnecessary pure-python modules
# removed_modules = docutils pygments PIL pkg_resources requests setuptools

# (list) python-for-android blacklist requirements
# List of python packages that shouldn't be included, even if they are a dependency
# p4a.extra_args = --blacklist-requirements=docutils,pygments,PIL,pkg_resources,requests,setuptools

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/icon.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (list) Permissions
android.permissions = BIND_NOTIFICATION_LISTENER_SERVICE,
    INTERNET,
    PACKAGE_USAGE_STATS,
    QUERY_ALL_PACKAGES,
    SYSTEM_ALERT_WINDOW,
    MEDIA_CONTENT_CONTROL,
    FOREGROUND_SERVICE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# 빌드 속도 향상을 위해 SDK 업데이트 건너뛰기
# android.skip_update = True

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# 빌드 최적화 설정
android.gradle_dependencies =
p4a.local_recipes =
p4a.num_workers = 4

# 디버그 빌드 사용 (빌드 속도 향상)
android.release = False
android.debug = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) The main file to start
android.app_main = main.py

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter together with android.entrypoint to set custom Java class instead of PythonActivity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_xml = ./src/android/extra_manifest.xml

# (str) Extra xml to write directly inside the <manifest><application> tag of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML arguments:
#android.extra_manifest_application_arguments = ./src/android/extra_manifest_application_arguments.xml

# (list) architecture to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# NDK 빌드 최적화
android.ndk_api = 21

# (str) python-for-android branch to use, defaults to master
p4a.branch = master

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (str) python-for-android source directory
p4a.source_dir = .buildozer/android/platform/python-for-android

# 빌드 캐시 설정
android.cache_builds = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1