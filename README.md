# AutoPCR Android 移植项目

将 AutoPCR 后端+Web前端整合为 Android 移动应用。

## 项目结构

```
autopcr-android/
├── src/                          # 源代码
│   ├── main.py                   # Android主入口
│   ├── service.py                # 后台服务
│   ├── autopcr/                  # 后端代码
│   │   ├── constants.py          # 适配Android路径
│   │   ├── http_server/          # Web服务器
│   │   │   └── ClientApp/        # 前端静态文件
│   │   └── ...
│   └── data/                     # 数据文件
│       ├── extraDrops.json
│       ├── rainbow.json
│       └── 微软雅黑.ttf
├── buildozer.spec                # 打包配置
└── README.md                     # 本文件
```

## 构建步骤

### 1. 安装依赖

在 Linux 或 WSL 环境下执行：

```bash
# 安装系统依赖
sudo apt update
sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk

# 安装 Buildozer
pip3 install buildozer cython

# 安装 Android SDK/NDK (首次运行会自动下载)
buildozer android debug
```

### 2. 项目配置

已配置的关键选项：

- **Python 版本**: 3.10.13
- **API 级别**: 33 (Android 13)
- **最低 API**: 21 (Android 5.0)
- **架构**: arm64-v8a, armeabi-v7a
- **端口**: 13200 (本地访问)

### 3. 构建 APK

```bash
cd autopcr-android

# 调试版本
buildozer android debug

# 发布版本
buildozer android release
```

构建完成后，APK 文件位于 `./bin/` 目录。

### 4. 安装到设备

```bash
# 自动安装并运行
buildozer android debug deploy run

# 或手动安装
adb install bin/autopcr-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

## 使用说明

### 首次启动

1. 安装 APK 后点击应用图标
2. 应用会自动启动后端服务器
3. 等待状态显示"服务运行正常"
4. 点击"打开网页界面"按钮
5. 浏览器将打开 `http://127.0.0.1:13200/daily/`

### 功能特性

- ✅ 自动启动后端服务
- ✅ 内置 Web 前端界面
- ✅ 本地 SQLite 数据库
- ✅ 定时任务支持
- ✅ 数据持久化存储

## 注意事项

### 依赖兼容性

部分 Python 包可能需要特殊处理：

1. **Pillow**: 需要 PIL recipe，buildozer 会自动处理
2. **pycryptodome**: 纯Python实现，正常支持
3. **SQLAlchemy**: 纯Python，正常支持
4. **bili-ticket-gt-python**: 如有C扩展需预编译

### 路径适配

代码已适配 Android 路径：

```python
# constants.py
if 'ANDROID_ARGUMENT' in os.environ:
    from android.storage import app_storage_path
    ROOT_DIR = app_storage_path()
else:
    ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
```

### 权限说明

应用需要以下权限：

- `INTERNET`: 网络访问
- `ACCESS_NETWORK_STATE`: 网络状态检测
- `WRITE_EXTERNAL_STORAGE`: 数据存储 (可选)

## 故障排除

### 构建失败

1. **内存不足**: 增加 Gradle 内存配置
   ```
   android.gradle_options = org.gradle.jvmargs=-Xmx4096M
   ```

2. **依赖缺失**: 检查 requirements 列表

3. **Recipe 错误**: 更新 p4a 版本
   ```
   buildozer android clean
   buildozer android update
   ```

### 运行时问题

1. **服务未启动**: 检查日志 `adb logcat | grep python`

2. **数据库错误**: 确保目录权限正确

3. **Web 无法访问**: 确认端口未被占用

## 开发调试

### 查看日志

```bash
# 实时查看
adb logcat -s python:D

# 保存到文件
adb logcat -d > logcat.txt
```

### 本地测试

```bash
cd src
python main.py
```

## 发布准备

### 签名配置

1. 生成密钥库：
   ```bash
   keytool -genkey -v -keystore autopcr.keystore -alias autopcr -keyalg RSA -keysize 2048 -validity 10000
   ```

2. 配置 buildozer.spec：
   ```
   android.signing.keystore = autopcr.keystore
   android.signing.alias = autopcr
   ```

### 应用图标

准备以下尺寸的图标：

- mipmap-mdpi: 48x48
- mipmap-hdpi: 72x72
- mipmap-xhdpi: 96x96
- mipmap-xxhdpi: 144x144
- mipmap-xxxhdpi: 192x192

## 技术栈

- **框架**: Kivy + Buildozer
- **后端**: Python 3.10 + Quart
- **前端**: React (静态构建)
- **数据库**: SQLite
- **打包**: Python-for-Android

## 许可证

与原项目保持一致。

## 更新日志

### v1.0.0
- 初始 Android 移植版本
- 整合后端服务和 Web 前端
- 支持一键启动运行
