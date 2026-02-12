[app]

# 应用标题
title = AutoPCR

# 包名
package.name = autopcr

# 包域名
package.domain = com.autopcr

# 源代码目录
source.dir = src

# 主程序入口
source.include_exts = py,png,jpg,kv,atlas,ttf,json,html,js,css,svg,txt,db

# 版本号
version = 1.0.0

# 依赖项 - 显式指定pyjnius版本避免Python 3兼容性问题
requirements = python3,kivy,pyjnius==1.6.1

# Android API版本
android.api = 33

# 最低API版本
android.minapi = 21

# NDK版本
android.ndk = 25b

# 支持的架构
android.archs = arm64-v8a

# 权限声明
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# 屏幕方向
orientation = portrait

# 全屏模式
fullscreen = 0

# Android gradle选项
android.gradle_options = org.gradle.jvmargs=-Xmx4096M

# 日志级别
android.logcat_filters = *:S python:D

# 启用AndroidX
android.enable_androidx = True

# 构建目录
build_dir = ./.buildozer

# 二进制文件目录
bin_dir = ./bin

# 构建模式
mode = debug

# 日志级别
log_level = 2

# 接受SDK许可
android.accept_sdk_license = True

[buildozer]

# 警告为错误
warn_on_root = 1
