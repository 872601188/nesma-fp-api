# Git 推送使用指南

## 快速推送（推荐方式）

### 方式一：使用 PowerShell 脚本（推荐）

1. **在项目根目录**，右键点击 `git-push.ps1` 文件
2. 选择 **"使用 PowerShell 运行"**
3. 按提示输入提交描述
4. 选择是否需要详细说明
5. 完成推送

**特点：**
- ✅ 彩色输出，清晰易读
- ✅ 交互式输入提交信息
- ✅ 支持多行详细说明
- ✅ 步骤清晰，防止误操作

---

### 方式二：使用批处理脚本

1. **双击运行** `git-push-helper.bat`
2. 按提示操作即可

---

### 方式三：手动命令行

如果你更习惯命令行，可以使用以下命令：

```bash
# 1. 查看变更
git status

# 2. 添加文件
git add -A

# 3. 提交（输入你的描述）
git commit -m "feat: 新增某某功能"

# 4. 推送
git push origin main
```

---

## 提交信息规范

好的提交信息方便后续查看历史，建议遵循以下格式：

### 格式
```
<类型>: <简短描述>

<详细说明（可选）>
```

### 常用类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 新增句子分割模式` |
| `fix` | 修复bug | `fix: 修复段落分割错误` |
| `refactor` | 代码重构 | `refactor: 优化分析器性能` |
| `docs` | 文档更新 | `docs: 更新API文档` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖包` |

### 示例

**简单提交：**
```
feat: 新增篇章分割模式
```

**详细提交：**
```
feat: 新增批量分析流式响应

- 添加 SSE 端点实现实时进度推送
- 前端添加进度条和步骤指示器
- 支持句子/段落/章节三种分割模式
```

---

## 查看提交历史

```bash
# 简洁历史
git log --oneline -10

# 详细历史
git log -5

# 图形化历史
git log --oneline --graph -10
```

---

## 常见问题

### Q: 提交时提示 "Author identity unknown"

**解决：** 运行以下命令配置身份
```bash
git config user.email "872601188@qq.com"
git config user.name "Your Name"
```

### Q: 推送时提示需要输入密码

**解决：** 使用 GitHub Personal Access Token 作为密码

或者配置凭据管理器：
```bash
git config --global credential.helper manager
```

### Q: 如何撤销上次提交？

```bash
# 撤销提交但保留修改
git reset --soft HEAD~1

# 撤销提交并丢弃修改（慎用！）
git reset --hard HEAD~1
```

### Q: 修改上次提交信息

```bash
git commit --amend -m "新的提交信息"
git push origin main --force-with-lease
```

---

## 建议工作流程

1. **修改代码** → 完成开发
2. **运行测试** → 确保功能正常
3. **运行推送脚本** → `git-push.ps1`
4. **输入提交描述** → 说明本次修改
5. **确认推送** → 完成

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `git-push.ps1` | PowerShell 推送脚本（推荐） |
| `git-push-helper.bat` | 批处理推送脚本 |
| `GIT_PUSH_GUIDE.md` | 本使用指南 |

---

**提示：** 推荐使用 `git-push.ps1` 脚本，它会引导你完成整个推送流程！
