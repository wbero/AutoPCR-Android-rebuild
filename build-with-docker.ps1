#!/usr/bin/env pwsh
# AutoPCR Android 构建脚本 (Docker)
# 使用方法: .\build-with-docker.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AutoPCR Android APK 构建工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker
Write-Host "[1/5] 检查 Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "  ✓ Docker 已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 错误: 未找到 Docker" -ForegroundColor Red
    Write-Host "  请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

# 检查 Docker 是否运行
try {
    docker info >$null 2>&1
    Write-Host "  ✓ Docker 正在运行" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 错误: Docker 未启动" -ForegroundColor Red
    Write-Host "  请先启动 Docker Desktop" -ForegroundColor Cyan
    exit 1
}

# 确保在正确目录
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host ""
Write-Host "[2/5] 项目信息" -ForegroundColor Yellow
Write-Host "  项目目录: $projectDir" -ForegroundColor Gray

# 检查必要文件
$requiredFiles = @("buildozer.spec", "src/main.py", "docker/Dockerfile.build")
$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "  ✗ 错误: 缺少必要文件:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "    - $file" -ForegroundColor Red
    }
    exit 1
}

Write-Host "  ✓ 所有必要文件已找到" -ForegroundColor Green

# 创建缓存目录（加速后续构建）
Write-Host ""
Write-Host "[3/5] 设置构建缓存..." -ForegroundColor Yellow

$cacheDir = Join-Path $projectDir ".buildozer-cache"
$androidPackagesDir = Join-Path $cacheDir "android-packages"

if (-not (Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
    Write-Host "  创建缓存目录: $cacheDir" -ForegroundColor Gray
}

if (-not (Test-Path $androidPackagesDir)) {
    New-Item -ItemType Directory -Path $androidPackagesDir -Force | Out-Null
    Write-Host "  创建Android包缓存目录" -ForegroundColor Gray
}

Write-Host "  ✓ 缓存设置完成" -ForegroundColor Green

# 构建 Docker 镜像
Write-Host ""
Write-Host "[4/5] 构建 Docker 镜像..." -ForegroundColor Yellow

docker build -t autopcr-builder -f docker/Dockerfile.build .

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ 错误: Docker 镜像构建失败" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Docker 镜像构建完成" -ForegroundColor Green

# 运行构建容器
Write-Host ""
Write-Host "[5/5] 开始构建 APK..." -ForegroundColor Yellow
Write-Host "  提示: 首次构建需要下载Android SDK/NDK，可能需要15-30分钟" -ForegroundColor Cyan
Write-Host "  请耐心等待..." -ForegroundColor Cyan
Write-Host ""

$buildStartTime = Get-Date

# 运行构建（挂载缓存目录以加速）
docker run --rm `
    -v "${PWD}:/app" `
    -v "${cacheDir}:/root/.buildozer" `
    autopcr-builder

$buildExitCode = $LASTEXITCODE
$buildEndTime = Get-Date
$buildDuration = $buildEndTime - $buildStartTime

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($buildExitCode -eq 0) {
    Write-Host "   ✓ 构建成功!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "构建耗时: $($buildDuration.ToString('hh\:mm\:ss'))" -ForegroundColor Gray
    
    # 检查输出
    $binDir = Join-Path $projectDir "bin"
    if (Test-Path $binDir) {
        $apkFiles = Get-ChildItem -Path $binDir -Filter "*.apk" | Sort-Object LastWriteTime -Descending
        if ($apkFiles.Count -gt 0) {
            Write-Host ""
            Write-Host "生成的APK文件:" -ForegroundColor Green
            foreach ($apk in $apkFiles) {
                $size = [math]::Round($apk.Length / 1MB, 2)
                Write-Host "  📱 $($apk.Name)" -ForegroundColor White
                Write-Host "     路径: $($apk.FullName)" -ForegroundColor Gray
                Write-Host "     大小: ${size} MB" -ForegroundColor Gray
                Write-Host ""
            }
            
            Write-Host "安装到设备:" -ForegroundColor Cyan
            Write-Host "  adb install $($apkFiles[0].FullName)" -ForegroundColor Gray
        } else {
            Write-Host "  ⚠ 未找到APK文件，请检查构建日志" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠ bin目录不存在" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ 构建失败 (退出码: $buildExitCode)" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "常见错误及解决方案:" -ForegroundColor Yellow
    Write-Host "  1. 内存不足: 增加Docker内存限制到4GB以上" -ForegroundColor Gray
    Write-Host "  2. 网络问题: 检查网络连接，或配置Docker代理" -ForegroundColor Gray
    Write-Host "  3. 依赖错误: 检查buildozer.spec中的requirements" -ForegroundColor Gray
    Write-Host ""
    Write-Host "查看详细日志:" -ForegroundColor Cyan
    Write-Host "  docker run --rm -v `"${PWD}:/app`" autopcr-builder buildozer android debug 2>&1 | Tee-Object build.log" -ForegroundColor Gray
}

Write-Host ""
Write-Host "构建完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
