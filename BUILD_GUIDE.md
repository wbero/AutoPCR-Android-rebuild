# AutoPCR Android 构建指南 - 无 Linux/WSL 方案

## 方案一：使用 Docker Desktop（推荐）

### 1. 安装 Docker Desktop

1. 下载 Docker Desktop for Windows:
   https://www.docker.com/products/docker-desktop

2. 安装并启动 Docker Desktop

3. 确保 Docker 正常运行：
   ```powershell
   docker --version
   ```

### 2. 创建 Dockerfile

已创建 `docker/Dockerfile.build`：

```dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake \
    && rm -rf /var/lib/apt/lists/*

# 安装 buildozer
RUN pip3 install buildozer cython

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 构建命令
CMD ["buildozer", "android", "debug"]
```

### 3. 使用 Docker 构建

在项目根目录创建 `build-with-docker.ps1`：

```powershell
# 构建 Docker 镜像
docker build -t autopcr-builder -f docker/Dockerfile.build .

# 运行构建容器
docker run --rm -v ${PWD}:/app autopcr-builder

# 或交互式构建
docker run --rm -it -v ${PWD}:/app autopcr-builder bash
```

运行构建：
```powershell
.\build-with-docker.ps1
```

构建完成后，APK 文件将在 `./bin/` 目录中。

---

## 方案二：使用 GitHub Actions（云构建）

### 1. 创建 GitHub 仓库

1. 将项目上传到 GitHub
2. 确保包含所有代码文件

### 2. 配置 GitHub Actions

已创建 `.github/workflows/build-android.yml`：

```yaml
name: Build Android APK

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          python3-pip \
          python3-venv \
          git \
          zip \
          unzip \
          openjdk-17-jdk \
          autoconf \
          libtool \
          pkg-config \
          zlib1g-dev \
          libncurses5-dev \
          libncursesw5-dev \
          libtinfo5 \
          cmake \
          libffi-dev \
          libssl-dev \
          automake
        pip3 install buildozer cython
    
    - name: Build APK
      run: |
        cd autopcr-android
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: autopcr-apk
        path: autopcr-android/bin/*.apk
```

### 3. 使用方法

1. 推送代码到 GitHub
2. 进入 GitHub 仓库页面
3. 点击 "Actions" 标签
4. 选择 "Build Android APK" 工作流
5. 点击 "Run workflow" 手动触发构建
6. 构建完成后，在 Artifacts 中下载 APK

---

## 方案三：使用在线构建服务

### 1. Buildozer Cloud (第三方)

一些第三方服务提供在线APK构建：

- **Kivy Buildozer Online**: 搜索 "Kivy Buildozer Online"
- **Python-for-Android Cloud**: 搜索 "P4A Cloud Builder"

### 2. 使用 Google Colab

创建 Colab 笔记本进行构建：

```python
# 在 Google Colab 中运行
!apt-get update
!apt-get install -y git zip unzip openjdk-17-jdk
!pip install buildozer cython

# 克隆项目
!git clone https://github.com/yourusername/autopcr-android.git
%cd autopcr-android

# 构建
!buildozer android debug

# 下载APK
from google.colab import files
files.download('bin/autopcr-1.0.0-arm64-v8a_armeabi-v7a-debug.apk')
```

---

## 方案四：Windows 本地 Python 运行（非APK）

如果只需要在Windows上运行，无需构建APK：

### 1. 创建 Windows 启动器

已创建 `run-windows.bat`：

```batch
@echo off
chcp 65001
echo [AutoPCR] 正在启动...

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10
    pause
    exit /b 1
)

:: 安装依赖
echo [AutoPCR] 检查依赖...
pip install -r requirements.txt -q

:: 启动应用
echo [AutoPCR] 启动服务...
cd src
python main.py

pause
```

### 2. 创建 PyInstaller 可执行文件

将Python项目打包为Windows exe：

```powershell
# 安装 PyInstaller
pip install pyinstaller

# 创建 spec 文件
pyi-makespec --onefile --windowed --name AutoPCR src/main.py

# 打包
pyinstaller AutoPCR.spec
```

---

## 方案对比

| 方案 | 难度 | 速度 | 适用场景 |
|------|------|------|----------|
| Docker Desktop | 低 | 中 | 有Docker环境的Windows用户 |
| GitHub Actions | 低 | 慢 | 有GitHub账号，不着急的用户 |
| 在线构建 | 中 | 快 | 临时构建需求 |
| Windows本地 | 低 | 快 | 只需要Windows运行 |

---

## 推荐方案

### 对于开发者：
1. **安装 Docker Desktop** → 使用方案一
2. 本地构建，完全控制

### 对于普通用户：
1. **使用 GitHub Actions** → 方案二
2. 无需安装任何软件
3. 我帮您构建并提供下载链接

### 如果您急需APK：
我可以帮您：
1. 将代码推送到我的GitHub仓库
2. 使用GitHub Actions构建
3. 提供APK下载链接

---

## 快速开始

### 使用 Docker（推荐）

```powershell
# 1. 安装 Docker Desktop
# 下载: https://www.docker.com/products/docker-desktop

# 2. 在项目目录打开 PowerShell

# 3. 运行构建
docker build -t autopcr-builder -f docker/Dockerfile.build .
docker run --rm -v ${PWD}:/app autopcr-builder

# 4. 获取APK
# 在 .\bin\ 目录中找到APK文件
```

### 使用 GitHub Actions

```powershell
# 1. 创建GitHub仓库并上传代码

# 2. 在GitHub页面点击 Actions → Build Android APK → Run workflow

# 3. 等待约10-15分钟

# 4. 下载构建好的APK
```

---

## 故障排除

### Docker 构建失败

1. **内存不足**：增加Docker内存限制到4GB以上
2. **网络问题**：配置Docker使用国内镜像源
3. **权限问题**：以管理员身份运行PowerShell

### GitHub Actions 失败

1. 检查代码是否完整上传
2. 查看Actions日志定位错误
3. 可能是依赖问题，检查requirements

---

## 需要帮助？

如果您遇到任何问题，可以：

1. 提供错误日志，我帮您分析
2. 我直接帮您构建APK（需要您提供代码或访问权限）
3. 创建预构建的Docker镜像，您直接下载使用
