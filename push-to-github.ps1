# 推送到GitHub并使用Actions构建
# 需要先在GitHub创建仓库

Write-Host "========================================"
Write-Host "   推送到GitHub并使用Actions构建"
Write-Host "========================================"
Write-Host ""

# 检查git
Write-Host "[1/4] 检查Git..."
try {
    git --version | Out-Null
    Write-Host "  Git已安装"
} catch {
    Write-Host "  请先安装Git: https://git-scm.com/download/win"
    exit 1
}

# 初始化git仓库
Write-Host ""
Write-Host "[2/4] 初始化Git仓库..."
if (-not (Test-Path .git)) {
    git init
    Write-Host "  Git仓库已初始化"
} else {
    Write-Host "  Git仓库已存在"
}

# 添加文件
Write-Host ""
Write-Host "[3/4] 添加文件到Git..."
git add .
git commit -m "Initial commit for Android build" -q
Write-Host "  文件已提交"

# 提示用户添加远程仓库
Write-Host ""
Write-Host "[4/4] 推送到GitHub..."
Write-Host ""
Write-Host "请先在GitHub创建仓库:"
Write-Host "  1. 访问 https://github.com/new"
Write-Host "  2. 输入仓库名: autopcr-android"
Write-Host "  3. 选择 Public 或 Private"
Write-Host "  4. 点击 Create repository"
Write-Host ""
Write-Host "然后运行以下命令:"
Write-Host "  git remote add origin https://github.com/你的用户名/autopcr-android.git"
Write-Host "  git branch -M main"
Write-Host "  git push -u origin main"
Write-Host ""
Write-Host "推送后，GitHub Actions会自动构建APK"
Write-Host "访问: https://github.com/你的用户名/autopcr-android/actions"
Write-Host ""
