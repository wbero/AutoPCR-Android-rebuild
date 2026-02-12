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

# 依赖项 (按字母顺序排列，便于管理)
requirements = python3==3.10.13,
    aiohttp,
    aiofile,
    aiosignal,
    async_timeout,
    attrs,
    brotli,
    certifi,
    cffi,
    charset_normalizer,
    click,
    cryptography,
    dataclasses_json,
    exceptiongroup,
    frozenlist,
    h11,
    h2,
    hpack,
    hypercorn,
    hyperframe,
    idna,
    itsdangerous,
    jinja2,
    kivy,
    markupsafe,
    marshmallow,
    msgpack,
    multidict,
    mypy_extensions,
    openpyxl,
    pillow,
    priority,
    pycparser,
    pycryptodome,
    pydantic,
    pyparsing,
    quart,
    quart_auth,
    quart_compress,
    quart_rate_limiter,
    requests,
    sqlalchemy,
    toml,
    typing_extensions,
    typing_inspect,
    urllib3,
    unitypy,
    werkzeug,
    wsproto,
    yarl,
    networkx,
    pulp,
    et_xmlfile,
    bili_ticket_gt_python

# Android API版本
android.api = 33

# 最低API版本
android.minapi = 21

# 目标API版本
android.sdk = 33

# NDK版本
android.ndk = 25b

# 支持的架构
android.archs = arm64-v8a, armeabi-v7a

# 权限声明
android.permissions = INTERNET,
    ACCESS_NETWORK_STATE,
    ACCESS_WIFI_STATE,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    FOREGROUND_SERVICE

# 应用图标 (需要准备不同尺寸的图标)
# icon.filename = %(source.dir)s/assets/icon.png

# 启动画面
# presplash.filename = %(source.dir)s/assets/presplash.png

# 屏幕方向
orientation = portrait

# 全屏模式
fullscreen = 0

# Android服务
android.services = AutopcrServer:src/service.py:foreground

# 额外Java类
# android.add_src =

# 添加资源文件
android.add_assets = src/autopcr/http_server/ClientApp:web

# 添加资源
# android.add_resources =

# Android gradle选项
android.gradle_options = org.gradle.jvmargs=-Xmx4096M

# 日志级别
android.logcat_filters = *:S python:D

# 启用AndroidX
android.enable_androidx = True

# 添加Java类路径
# android.add_aars =

# 保留Python模块
android.whitelist = 
    encodings,
    asyncio,
    collections,
    concurrent,
    ctypes,
    email,
    html,
    http,
    json,
    logging,
    multiprocessing,
    pathlib,
    pickle,
    sqlite3,
    ssl,
    urllib,
    xml,
    xmlrpc,
    uuid,
    typing,
    dataclasses,
    enum,
    hashlib,
    base64,
    binascii,
    copy,
    datetime,
    decimal,
    fractions,
    functools,
    inspect,
    io,
    itertools,
    keyword,
    linecache,
    math,
    numbers,
    operator,
    os,
    posixpath,
    pprint,
    random,
    re,
    reprlib,
    secrets,
    string,
    struct,
    subprocess,
    sys,
    tempfile,
    textwrap,
    threading,
    time,
    tokenize,
    traceback,
    types,
    warnings,
    weakref

# 保留文件
android.p4a_local_recipes =

# p4a分支
android.p4a_branch = master

# p4a版本
android.p4a_version = master

# p4a源码
android.p4a_source_dir =

[buildozer]

# 构建模式 (debug/release)
mode = debug

# 日志级别
log_level = 2

# 警告为错误
warn_on_root = 1

# 构建目录
build_dir = ./.buildozer

# 二进制文件目录
bin_dir = ./bin

# 是否安装到设备
install_into_device = 0

# 设备ID
android.accept_sdk_license = True

# 是否使用私有存储
android.private_storage = True
