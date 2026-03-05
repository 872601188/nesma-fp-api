# NESMA 项目 Git 推送助手
# 使用方式: 右键点击 -> 使用 PowerShell 运行

$ErrorActionPreference = "Stop"

function Show-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   NESMA 项目 Git 推送助手" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Get-GitStatus {
    $status = git status --porcelain
    return $status
}

function Show-GitStatus {
    Write-Host "[步骤 1/4] 当前文件变更状态：" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    git status -s
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host ""
}

function Add-Files {
    Write-Host "[步骤 2/4] 准备添加文件到暂存区..." -ForegroundColor Yellow
    git add -A
    Write-Host "[✓ 完成] 所有变更已添加到暂存区" -ForegroundColor Green
    Write-Host ""
}

function Show-StagedFiles {
    Write-Host "[步骤 3/4] 即将提交的文件：" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    git diff --cached --stat
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host ""
}

function Get-CommitMessage {
    Write-Host "[步骤 4/4] 请输入本次修改的描述" -ForegroundColor Yellow
    Write-Host "提示：简要说明本次修改的内容，例如：" -ForegroundColor Gray
    Write-Host "  - feat: 新增用户登录功能" -ForegroundColor DarkGray
    Write-Host "  - fix: 修复数据导出bug" -ForegroundColor DarkGray
    Write-Host "  - refactor: 优化查询性能" -ForegroundColor DarkGray
    Write-Host ""
    
    $global:commitMsg = Read-Host "提交描述"
    
    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
        Write-Host "[✗ 错误] 提交描述不能为空！" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
}

function Get-CommitDetails {
    Write-Host "是否需要添加详细说明？" -ForegroundColor Yellow
    Write-Host "1. 简短提交（仅使用上述描述）"
    Write-Host "2. 详细提交（添加修改详情）"
    Write-Host ""
    
    $choice = Read-Host "选择 (1/2，默认 1)"
    
    if ($choice -eq "2") {
        Write-Host ""
        Write-Host "请输入详细修改内容（输入 END 结束）：" -ForegroundColor Yellow
        Write-Host "----------------------------------------" -ForegroundColor Gray
        
        $lines = @()
        while ($true) {
            $line = Read-Host "> "
            if ($line -eq "END") { break }
            if (-not [string]::IsNullOrWhiteSpace($line)) {
                $lines += $line
            }
        }
        
        $global:detailMsg = $lines -join "`n"
        return $true
    }
    
    return $false
}

function Commit-Changes {
    param([bool]$hasDetail)
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "正在提交..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    if ($hasDetail -and $global:detailMsg) {
        # 使用 Here-String 创建提交信息
        $fullMsg = @"
$global:commitMsg

详细修改：
$global:detailMsg
"@
        $fullMsg | git commit -F -
    } else {
        git commit -m "$global:commitMsg"
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[✗ 错误] 提交失败！" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[✓ 提交成功]" -ForegroundColor Green
    Write-Host ""
}

function Push-ToGitHub {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "[步骤 5/5] 推送到 GitHub..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  [✓ 成功] 代码已推送到 GitHub！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "提交信息: $global:commitMsg" -ForegroundColor Cyan
        
        # 显示最近提交
        Write-Host ""
        Write-Host "最近提交历史：" -ForegroundColor Yellow
        git log --oneline -3 --decorate
    } else {
        Write-Host ""
        Write-Host "[✗ 错误] 推送失败！" -ForegroundColor Red
        Write-Host "请检查网络连接或凭据。" -ForegroundColor Red
    }
}

# ============ 主程序 ============

Show-Header

# 切换到脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 检查是否有变更
$status = Get-GitStatus
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "[提示] 没有发现文件变更，无需推送。" -ForegroundColor Green
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 0
}

Show-GitStatus
Add-Files
Show-StagedFiles
Get-CommitMessage
$hasDetail = Get-CommitDetails
Commit-Changes -hasDetail $hasDetail
Push-ToGitHub

Write-Host ""
Read-Host "按 Enter 键退出"
