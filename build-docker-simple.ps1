# AutoPCR Android 构建脚本 (简化版)
# 使用方法: .\build-docker-simple.ps1

Write-Host "========================================"
Write-Host "   AutoPCR Android APK 构建工具"
Write-Host "========================================"
Write-Host ""

# 检查 Docker
Write-Host "[1/3] 检查 Docker..."
try {
    docker --version | Out-Null
    Write-Host "  Docker 已安装"
} catch {
    Write-Host "  错误: 未找到 Docker，请先安装 Docker Desktop"
    exit 1
}

# 检查 Docker 是否运行
try {
    docker info > $null 2>&1
    Write-Host "  Docker 正在运行"
} catch {
    Write-Host "  错误: Docker 未启动，请先启动 Docker Desktop"
    exit 1
}

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host ""
Write-Host "[2/3] 构建 Docker 镜像..."
docker build -t autopcr-builder -f docker/Dockerfile.build .

if ($LASTEXITCODE -ne 0) {
    Write-Host "  错误: Docker 镜像构建失败"
    exit 1
}
Write-Host "  Docker 镜像构建完成"

Write-Host ""
Write-Host "[3/3] 开始构建 APK..."
Write-Host "  提示: 首次构建需要15-30分钟，请耐心等待..."
Write-Host ""

$buildStartTime = Get-Date

# 运行构建
docker run --rm -v "${PWD}:/app" autopcr-builder

$buildExitCode = $LASTEXITCODE
$buildEndTime = Get-Date
$buildDuration = $buildEndTime - $buildStartTime

Write-Host ""
Write-Host "========================================"

if ($buildExitCode -eq 0) {
    Write-Host "   构建成功!"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "构建耗时: $($buildDuration.ToString('hh\:mm\:ss'))"
    
    $binDir = Join-Path $projectDir "bin"
    if (Test-Path $binDir) {
        $apkFiles = Get-ChildItem -Path $binDir -Filter "*.apk"
        if ($apkFiles.Count -gt 0) {
            Write-Host ""
            Write-Host "生成的APK文件:"
            foreach ($apk in $apkFiles) {
                $size = [math]::Round($apk.Length / 1MB, 2)
                Write-Host "  - $($apk.Name) (${size} MB)"
            }
            Write-Host ""
            Write-Host "安装命令: adb install $($apkFiles[0].FullName)"
        }
    }
} else {
    Write-Host "   构建失败 (退出码: $buildExitCode)"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "常见错误:"
    Write-Host "  1. 内存不足: 增加Docker内存到4GB以上"
    Write-Host "  2. 网络问题: 检查网络连接"
    Write-Host "  3. 依赖错误: 检查buildozer.spec配置"
}

Write-Host ""
Write-Host "完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
