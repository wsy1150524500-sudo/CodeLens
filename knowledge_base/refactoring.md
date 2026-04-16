# 重构手法

## 提取与内联

### 提取函数（Extract Function）
- 触发条件：函数过长、代码块有注释说明其意图、同一段逻辑重复出现
- 做法：将代码块提取为独立函数，用函数名替代注释
- 提取后函数应该能独立理解，不依赖大量外部上下文

### 提取变量（Extract Variable）
- 触发条件：复杂表达式难以理解
- 做法：将子表达式赋值给有意义的临时变量
- 示例：`if (date.before(SUMMER_START) || date.after(SUMMER_END))` → `isNotSummer`

### 内联函数/变量（Inline）
- 触发条件：函数体和函数名一样清晰，中间变量没有增加可读性
- 过度提取反而增加跳转成本，适当内联

## 简化条件逻辑

### 卫语句（Guard Clause）
- 将异常条件提前 return/throw，减少嵌套
- 反面：if valid { if hasPermission { if notExpired { ...doWork... } } }
- 正面：if !valid return; if !hasPermission return; if expired return; doWork()

### 合并条件表达式
- 多个条件导致相同结果时，合并为一个函数
- `if (isOld) return 0; if (isSick) return 0;` → `if (isUninsurable()) return 0;`

### 用多态替代条件
- 根据类型做不同处理的 switch/if-else，改为多态（子类重写方法）
- 或使用策略模式 + 映射表

## 数据组织

### 引入参数对象（Introduce Parameter Object）
- 多个函数共享同一组参数时，封装为类/结构体
- `createOrder(userId, userName, userEmail)` → `createOrder(user)`

### 用对象替代基本类型（Replace Primitive with Object）
- 电话号码、金额、坐标等有业务含义的值，封装为值对象
- 可以附加校验逻辑和格式化方法

## 重构安全守则

- 每次只做一个小改动，改完立即运行测试
- 有测试覆盖才重构，没有测试先补测试
- 重构不改变外部行为，只改善内部结构
- 使用 IDE 的自动重构功能（Rename、Extract、Move）减少手动出错
- 提交粒度要小：一次提交一个重构手法，方便 review 和回滚
