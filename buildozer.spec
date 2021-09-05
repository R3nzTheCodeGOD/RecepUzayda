[app]
title = Recep Uzayda
package.name = RecepUzayda
package.domain = r3nzthecodegod.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,ttf
version = 0.31
requirements = python3,kivy==2.0.0,kivymd
icon.filename = %(source.dir)s/icon.png
orientation = landscape
osx.python_version = 3
osx.kivy_version = 2.0.0
fullscreen = 1
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

[buildozer]
log_level = 2
warn_on_root = 1