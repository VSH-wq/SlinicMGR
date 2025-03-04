[app]
# Application title and identifier
title = ClinicMGR
package.name = clinicmgr
package.domain = org.yourname

# Source directory and included file extensions
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,db

# Application version
version = 0.1

# Requirements and dependencies
requirements = 
    python3,
    kivy,
    kivymd,
    sqlite3,
    pillow,
    requests

# Android specific configurations
[android]
# Permissions your app needs
android.permissions = 
    INTERNET,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE

# Orientation and screen properties
orientation = portrait
fullscreen = 0

# Build configurations
[buildozer]
# Log level for build process
log_level = 2
warn_on_root = 1

# Additional Android configurations
android.api = 30
android.minapi = 24
android.sdk = 30

# App icon and splash screen (optional)
# icon.filename = path/to/your/icon.png
# presplash.filename = path/to/your/presplash.png
