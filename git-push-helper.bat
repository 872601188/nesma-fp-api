@echo off
chcp 65001 >nul
echo ========================================
echo   NESMA 项目 Git 推送助手
echo ========================================
echo.

REM 检查是否有变更
cd /d "%~dp0"
git diff --quiet HEAD
if %ERRORLEVEL% == 0 (
    echo [提示] 没有发现文件变更，无需推送。
    pause
    exit /b 0
)

echo [1/4] 当前文件变更状态：
echo ----------------------------------------
git status -s
echo ----------------------------------------
echo.

REM 检查是否已经 add
echo [2/4] 准备添加文件到暂存区...
git add -A
echo [完成] 所有变更已添加到暂存区
echo.

REM 显示即将提交的文件列表
echo [3/4] 即将提交的文件：
echo ----------------------------------------
git diff --cached --stat
echo ----------------------------------------
echo.

REM 输入提交信息
echo [4/4] 请输入本次修改的描述：
echo （简要说明本次修改的内容，例如：新增用户登录功能）
echo.
set /p commit_msg=提交描述: 

if "%commit_msg%"=="" (
    echo [错误] 提交描述不能为空！
    pause
    exit /b 1
)

REM 添加时间戳和详细说明选项
echo.
echo 是否需要添加详细说明？
echo 1. 简短提交（仅一行描述）
echo 2. 详细提交（包含修改详情）
set /p detail_choice=选择 (1/2): 

if "%detail_choice%"=="2" (
    echo.
    echo 请输入详细修改内容（多行，输入空行结束）：
    echo.
    
    set "detail_lines="
    :loop
    set /p line=^> 
    if "!line!"=="" goto :endinput
    set "detail_lines=!detail_lines!!line!\n"
    goto :loop
    :endinput
    
    git commit -m "%commit_msg%" -m "详细修改内容：" -m "%detail_lines%"
) else (
    git commit -m "%commit_msg%"
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 提交失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo [5/5] 推送到 GitHub...
echo ========================================
git push origin main

if %ERRORLEVEL% == 0 (
    echo.
    echo [成功] 代码已成功推送到 GitHub！
    echo 提交信息: %commit_msg%
) else (
    echo.
    echo [错误] 推送失败，请检查网络连接或凭据。
)

pause
