# 安全漏洞模式与防御

## 注入攻击

### SQL 注入
- 永远不要拼接 SQL 字符串，使用参数化查询或 ORM
- 反面示例：`"SELECT * FROM users WHERE id = " + userId`
- 正面示例：`cursor.execute("SELECT * FROM users WHERE id = ?", (userId,))`
- 存储过程也可能存在注入风险，参数仍需绑定

### 命令注入
- 避免将用户输入传入 shell 命令：os.system(), exec(), eval()
- 使用安全的 API 替代：subprocess.run() 配合参数列表而非字符串
- 白名单校验用户输入，拒绝特殊字符

### XSS（跨站脚本）
- 所有用户输入在输出到 HTML 前必须转义
- 使用模板引擎的自动转义功能
- Content-Security-Policy 头限制脚本来源
- 富文本场景使用白名单过滤而非黑名单

## 认证与授权

- 密码存储必须使用 bcrypt/scrypt/argon2 哈希，永远不要明文或 MD5/SHA
- JWT token 设置合理过期时间，敏感操作要求重新认证
- API 接口做权限校验，不要仅依赖前端隐藏按钮
- 避免水平越权：用户 A 不能通过修改 ID 访问用户 B 的数据
- 敏感操作加 CSRF token 防护

## 敏感信息保护

- API Key、数据库密码等绝不硬编码在源码中，使用环境变量或密钥管理服务
- .env 文件加入 .gitignore，永远不要提交到版本库
- 日志中脱敏处理：不打印密码、token、身份证号、手机号
- 错误信息不要暴露内部实现细节（堆栈、SQL 语句、文件路径）
- HTTPS 传输，禁用不安全的 TLS 版本

## 输入校验

- 所有外部输入都不可信：HTTP 参数、请求头、文件上传、第三方 API 返回
- 校验数据类型、长度、范围、格式
- 文件上传校验：文件类型白名单、大小限制、文件名消毒
- 反序列化风险：不要反序列化不可信数据（pickle、yaml.load、Java ObjectInputStream）
- 正则表达式防 ReDoS：避免嵌套量词如 (a+)+

## 依赖安全

- 定期扫描依赖漏洞：npm audit, pip-audit, snyk, dependabot
- 锁定依赖版本，避免自动升级引入恶意包
- 最小权限原则：只引入必要的依赖
- 关注 typosquatting 攻击：仔细核对包名拼写
