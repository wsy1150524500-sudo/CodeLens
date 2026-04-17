# Git 工作流与版本控制

## 提交规范

### Conventional Commits
- feat: 新功能
- fix: 修复 bug
- docs: 文档变更
- style: 代码格式（不影响逻辑）
- refactor: 重构（不是新功能也不是修 bug）
- perf: 性能优化
- test: 测试相关
- chore: 构建/工具/依赖变更
- 格式：type(scope): description
- 示例：feat(auth): 添加 JWT token 刷新机制

### 提交原则
- 每个提交只做一件事，原子性提交
- 提交信息用祈使句："添加用户认证" 而非 "添加了用户认证"
- 不要提交半成品代码到主分支
- 不要把不相关的改动放在同一个提交中
- 提交前 review 自己的 diff

## 分支策略

### Git Flow
- main：生产环境代码，只接受合并
- develop：开发主线，集成各功能分支
- feature/*：功能开发分支，从 develop 创建
- release/*：发布准备分支，从 develop 创建
- hotfix/*：紧急修复分支，从 main 创建
- 适合发布周期长、版本管理严格的项目

### GitHub Flow
- main 分支始终可部署
- 功能开发创建分支，完成后发 PR
- PR 通过 review 和 CI 后合并到 main
- 合并后自动部署
- 简单直接，适合持续部署的项目

### Trunk-Based Development
- 所有人直接在 main 分支开发
- 用 Feature Flag 控制未完成功能的可见性
- 频繁提交，小步快跑
- 适合高水平团队和持续集成环境

## Pull Request 最佳实践

- PR 尽量小：200-400 行改动，超过 500 行很难 review
- 标题清晰描述改动内容
- 描述中说明：为什么改、改了什么、怎么测试的
- 关联 Issue 编号
- 自己先 review 一遍再提交
- 及时回复 reviewer 的评论
- Squash merge 保持主分支历史整洁

## .gitignore 最佳实践

- IDE 配置文件：.idea/, .vscode/, *.swp
- 依赖目录：node_modules/, vendor/, .venv/
- 构建产物：dist/, build/, *.pyc, __pycache__/
- 环境配置：.env（提供 .env.example）
- 系统文件：.DS_Store, Thumbs.db
- 日志文件：*.log
- 使用 gitignore.io 生成模板

## 常见问题处理

### 撤销操作
- 撤销工作区修改：git checkout -- file
- 撤销暂存：git reset HEAD file
- 修改最后一次提交：git commit --amend
- 撤销已推送的提交：git revert（不要用 reset）

### 合并冲突
- 先理解双方的改动意图
- 不要盲目接受一方，手动合并逻辑
- 合并后运行测试确认功能正常
- 频繁合并主分支减少冲突概率

### 敏感信息泄露
- 如果提交了密钥/密码，立即轮换密钥
- git filter-branch 或 BFG Repo-Cleaner 清理历史
- 仅删除文件不够，历史中仍然存在
