# AutoPCR Android 快速构建指南

## 使用 Docker 构建（推荐）

### 前置要求
- ✅ Docker Desktop 已安装并运行
- ✅ 至少 4GB 可用内存
- ✅ 至少 10GB 可用磁盘空间

### 一键构建

在 PowerShell 中执行：

```powershell
cd autopcr-android
.\build-with-docker.ps1
```

### 手动构建（如果脚本失败）

```powershell
# 1. 进入项目目录
cd autopcr-android

# 2. 构建 Docker 镜像
docker build -t autopcr-builder -f docker/Dockerfile.build .

# 3. 运行构建（挂载缓存目录）
docker run --rm `
    -v "${PWD}:/app" `
    -v "${PWD}/.buildozer-cache:/root/.buildozer" `
    autopcr-builder
```

### 构建时间

- **首次构建**: 15-30分钟（需要下载Android SDK/NDK）
- **后续构建**: 5-10分钟（使用缓存）

### 获取APK

构建完成后，APK文件位于：
```
autopcr-android/bin/autopcr-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### 安装到手机

```powershell
# 使用 adb 安装
adb install bin/autopcr-1.0.0-arm64-v8a_armeabi-v7a-debug.apk

# 或手动复制到手机安装
```

---

## 常见问题

### Q: 构建过程中卡住？
A: 首次构建需要下载大量文件，请耐心等待。可以按 `Ctrl+T` 查看下载进度。

### Q: 内存不足错误？
A: 在 Docker Desktop 设置中增加内存限制：
- Settings → Resources → Memory → 设置为 4GB 或更高

### Q: 网络超时？
A: 配置Docker使用国内镜像源，或检查网络连接。

### Q: 如何重新构建？
A: 直接再次运行构建脚本，缓存会加速构建过程。

---

## 使用 GitHub Actions 构建（无需本地Docker）

1. 将代码推送到 GitHub 仓库
2. 访问仓库页面 → Actions → Build Android APK
3. 点击 "Run workflow"
4. 等待15-20分钟
5. 在 Artifacts 中下载 APK

---

## 构建成功后的下一步

1. **安装APK** 到Android设备
2. **启动应用**，等待服务启动
3. **点击"打开网页界面"**按钮
4. **开始使用** AutoPCR！

---

## 需要帮助？

如果遇到问题，请提供：
1. 错误日志截图
2. Docker版本信息：`docker --version`
3. 构建命令输出

可以通过以下方式获取帮助：
- 查看 [BUILD_GUIDE.md](BUILD_GUIDE.md) 详细文档
- 提交 GitHub Issue
- 联系项目维护者
