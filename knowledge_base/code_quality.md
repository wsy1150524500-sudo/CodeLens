# 代码质量通用原则

## 命名规范

- 变量名应表达意图，避免单字母命名（循环变量 i/j/k 除外）
- 函数名用动词开头，描述行为：getUserById 优于 user，validateInput 优于 check
- 布尔变量用 is/has/can/should 前缀：isValid, hasPermission, canRetry
- 常量全大写下划线分隔：MAX_RETRY_COUNT, DEFAULT_TIMEOUT
- 类名用名词，PascalCase：UserService, OrderRepository
- 避免缩写，除非是广泛认可的：url, http, id, config
- 避免在命名中包含类型信息：userList 不如 users，nameString 不如 name
- 枚举值用大写：Status.ACTIVE, Color.RED
- 接口名避免 I 前缀（Java/C# 习惯除外），用形容词或能力描述：Serializable, Comparable
- 包/模块名用小写，避免下划线：utils, models, services

## 函数设计

- 单一职责：一个函数只做一件事，函数名能完整描述它做的事
- 参数不超过 3 个，超过时用对象/结构体封装
- 函数体不超过 20-30 行，超过时考虑拆分
- 避免副作用：函数要么返回值，要么修改状态，不要两者都做
- 尽早返回（Guard Clause）：先处理异常情况 return，减少嵌套层级
- 避免 flag 参数：renderPage(true) 不如拆成 renderUserPage() 和 renderAdminPage()
- 纯函数优先：相同输入总是返回相同输出，不依赖外部状态，易于测试和推理
- 避免过长的参数列表，使用 Builder 模式或配置对象
- 函数应该在同一抽象层级上操作，不要混合高层逻辑和底层细节
- 错误处理和正常逻辑分离，不要用异常控制流程

## 复杂度控制

- 圈复杂度（Cyclomatic Complexity）建议不超过 10
- 嵌套层级不超过 3 层，超过时用提前返回或提取函数
- 条件表达式过长时提取为有意义的布尔变量
- 避免深层回调嵌套（Callback Hell），使用 async/await 或 Promise 链
- switch/match 超过 5 个分支时考虑用策略模式或映射表替代
- 认知复杂度比圈复杂度更能反映代码可读性，关注嵌套和中断流程的结构
- 长方法拆分时优先提取"做什么"而非"怎么做"的部分
- 三元表达式嵌套不超过一层，否则用 if-else

## DRY 原则（Don't Repeat Yourself）

- 相同逻辑出现 2 次以上时提取为公共函数
- 但不要过度抽象：两段代码看起来相似但业务含义不同时，重复是可以接受的
- 配置值、魔法数字提取为常量
- 字符串模板优于字符串拼接
- 重复的错误处理逻辑可以用装饰器或中间件统一处理
- 数据转换逻辑如果多处使用，提取为专门的 mapper/converter

## 注释与文档

- 好代码自解释，注释解释"为什么"而不是"做了什么"
- 公共 API 必须有文档注释（参数、返回值、异常）
- TODO/FIXME/HACK 注释要附带原因和负责人
- 删除注释掉的代码，版本控制会保留历史
- 复杂算法或业务规则需要注释说明背景
- 正则表达式必须加注释说明匹配意图
- 接口文档用 OpenAPI/Swagger 规范，保持代码和文档同步

## 代码组织

- 文件长度建议不超过 300-500 行，过长时按职责拆分
- 相关的函数和类放在同一模块中，按功能而非类型组织目录
- 导入语句分组：标准库、第三方库、本地模块，各组之间空一行
- 避免循环依赖，如果出现说明模块划分有问题
- 公共接口放在文件顶部，私有实现放在底部
- 测试文件和源码文件保持相同的目录结构
