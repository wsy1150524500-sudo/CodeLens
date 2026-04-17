# 安全漏洞模式与防御

## 注入攻击

### SQL 注入
- 永远不要拼接 SQL 字符串，使用参数化查询或 ORM
- 反面示例：`"SELECT * FROM users WHERE id = " + userId`
- 正面示例（Python）：`cursor.execute("SELECT * FROM users WHERE id = ?", (userId,))`
- 正面示例（Java）：`PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id = ?"); ps.setInt(1, userId);`
- 存储过程也可能存在注入风险，参数仍需绑定
- ORM 的 raw query 功能同样需要参数化
- 二次注入：数据库中已存储的恶意数据被取出后拼接到新查询中

### 命令注入
- 避免将用户输入传入 shell 命令：os.system(), exec(), eval()
- 使用安全的 API 替代：subprocess.run() 配合参数列表而非字符串
- 白名单校验用户输入，拒绝特殊字符
- Node.js 中避免 child_process.exec()，使用 execFile() 或 spawn()
- Go 中使用 exec.Command() 的参数列表形式

### XSS（跨站脚本）
- 所有用户输入在输出到 HTML 前必须转义
- 使用模板引擎的自动转义功能（Vue 默认转义、React JSX 默认转义）
- Content-Security-Policy 头限制脚本来源
- 富文本场景使用白名单过滤而非黑名单（DOMPurify）
- 存储型 XSS 比反射型更危险，数据入库前也要校验
- HttpOnly Cookie 防止 JS 读取 session

### SSRF（服务端请求伪造）
- 不要让用户控制服务端发起请求的 URL
- 如果必须，白名单校验域名和 IP，禁止访问内网地址（127.0.0.1, 10.x, 172.16-31.x, 192.168.x）
- 禁用 HTTP 重定向跟随，或限制重定向次数

## 认证与授权

- 密码存储必须使用 bcrypt/scrypt/argon2 哈希，永远不要明文或 MD5/SHA
- JWT token 设置合理过期时间，敏感操作要求重新认证
- API 接口做权限校验，不要仅依赖前端隐藏按钮
- 避免水平越权：用户 A 不能通过修改 ID 访问用户 B 的数据
- 敏感操作加 CSRF token 防护
- 多因素认证（MFA）用于高安全场景
- 登录失败加速率限制，防止暴力破解
- Session 固定攻击：登录成功后重新生成 session ID
- OAuth 2.0 实现要验证 state 参数防止 CSRF
- API Key 不要放在 URL 参数中，用 Header 传递

## 敏感信息保护

- API Key、数据库密码等绝不硬编码在源码中，使用环境变量或密钥管理服务
- .env 文件加入 .gitignore，永远不要提交到版本库
- 日志中脱敏处理：不打印密码、token、身份证号、手机号
- 错误信息不要暴露内部实现细节（堆栈、SQL 语句、文件路径）
- HTTPS 传输，禁用不安全的 TLS 版本（TLS 1.0/1.1）
- 数据库连接字符串中的密码不要出现在日志或错误信息中
- Git 历史中如果曾经提交过密钥，需要轮换密钥而非仅删除文件
- 前端代码中不要存放任何密钥，前端代码对用户完全可见
- 加密存储敏感数据，使用 AES-256-GCM 等现代加密算法
- 密钥轮换机制：定期更换 API Key 和数据库密码

## 输入校验

- 所有外部输入都不可信：HTTP 参数、请求头、文件上传、第三方 API 返回
- 校验数据类型、长度、范围、格式
- 文件上传校验：文件类型白名单、大小限制、文件名消毒（去除路径遍历字符 ../ ）
- 反序列化风险：不要反序列化不可信数据（Python pickle、Java ObjectInputStream、PHP unserialize）
- 正则表达式防 ReDoS：避免嵌套量词如 (a+)+，使用超时机制
- 路径遍历防护：用户输入的文件名不能包含 ../ 或绝对路径
- 整数溢出：大数运算注意语言的整数范围限制
- 编码一致性：统一使用 UTF-8，防止编码绕过攻击
- JSON 解析设置最大深度和大小限制，防止 DoS

## 依赖安全

- 定期扫描依赖漏洞：npm audit, pip-audit, snyk, dependabot
- 锁定依赖版本（lock 文件），避免自动升级引入恶意包
- 最小权限原则：只引入必要的依赖
- 关注 typosquatting 攻击：仔细核对包名拼写
- 使用私有镜像源时确保源本身可信
- 容器镜像使用特定版本标签，不要用 latest
- 定期更新依赖，不要让漏洞累积

## 安全 HTTP 头

- Strict-Transport-Security：强制 HTTPS
- X-Content-Type-Options: nosniff：防止 MIME 类型嗅探
- X-Frame-Options: DENY：防止点击劫持
- Content-Security-Policy：限制资源加载来源
- X-XSS-Protection: 0：现代浏览器建议关闭（依赖 CSP）
- Referrer-Policy: strict-origin-when-cross-origin：控制 Referer 泄露
