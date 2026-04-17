# 重构手法

## 提取与内联

### 提取函数（Extract Function）
- 触发条件：函数过长、代码块有注释说明其意图、同一段逻辑重复出现
- 做法：将代码块提取为独立函数，用函数名替代注释
- 提取后函数应该能独立理解，不依赖大量外部上下文
- 如果需要传入太多参数，考虑提取为类的方法

### 提取变量（Extract Variable）
- 触发条件：复杂表达式难以理解
- 做法：将子表达式赋值给有意义的临时变量
- 示例：`if (date.before(SUMMER_START) || date.after(SUMMER_END))` → `isNotSummer`

### 提取类（Extract Class）
- 触发条件：一个类承担了太多职责，有两组不相关的字段和方法
- 做法：将相关的字段和方法移到新类中
- 判断标准：如果修改一组字段不影响另一组，说明应该拆分

### 内联函数/变量（Inline）
- 触发条件：函数体和函数名一样清晰，中间变量没有增加可读性
- 过度提取反而增加跳转成本，适当内联
- 只有一个调用点的简单函数可以考虑内联

## 简化条件逻辑

### 卫语句（Guard Clause）
- 将异常条件提前 return/throw，减少嵌套
- 反面：if valid { if hasPermission { if notExpired { ...doWork... } } }
- 正面：if !valid return; if !hasPermission return; if expired return; doWork()
- 每个卫语句处理一个异常情况，逻辑清晰

### 合并条件表达式
- 多个条件导致相同结果时，合并为一个函数
- `if (isOld) return 0; if (isSick) return 0;` → `if (isUninsurable()) return 0;`
- 合并后的函数名应该表达业务含义

### 用多态替代条件
- 根据类型做不同处理的 switch/if-else，改为多态（子类重写方法）
- 或使用策略模式 + 映射表
- 适用于分支逻辑稳定且各分支差异大的场景

### 分解条件表达式
- 复杂的 if-else 条件和分支体都提取为函数
- if (isSummer(date)) charge = summerCharge(); else charge = winterCharge();
- 让代码读起来像自然语言

### 用管道替代循环
- 用 map/filter/reduce 替代手写循环
- 链式调用更声明式，意图更清晰
- Python: 列表推导式、生成器表达式
- JavaScript: array.filter().map().reduce()

## 数据组织

### 引入参数对象（Introduce Parameter Object）
- 多个函数共享同一组参数时，封装为类/结构体
- `createOrder(userId, userName, userEmail)` → `createOrder(user)`
- 参数对象可以附加校验逻辑

### 用对象替代基本类型（Replace Primitive with Object）
- 电话号码、金额、坐标等有业务含义的值，封装为值对象
- 可以附加校验逻辑和格式化方法
- 金额用 Decimal 而非 float，避免精度问题

### 拆分变量（Split Variable）
- 一个变量被赋值多次用于不同目的，拆成多个变量
- 每个变量只赋值一次（不可变优先）
- 循环变量和累加器除外

### 封装集合（Encapsulate Collection）
- 不要直接暴露内部集合的引用
- 提供 add/remove/get 方法控制访问
- 返回集合的不可变视图或副本

## 移动特性

### 搬移函数（Move Function）
- 函数更多地使用另一个类的数据，应该搬到那个类中
- 判断标准：函数和哪个类的交互最多

### 搬移字段（Move Field）
- 字段被另一个类的方法频繁访问，搬到那个类中

### 以委托取代继承（Replace Inheritance with Delegation）
- 子类只用了父类的部分功能，改为组合 + 委托
- "is-a" 关系不成立时不要用继承

## 重构安全守则

- 每次只做一个小改动，改完立即运行测试
- 有测试覆盖才重构，没有测试先补测试
- 重构不改变外部行为，只改善内部结构
- 使用 IDE 的自动重构功能（Rename、Extract、Move）减少手动出错
- 提交粒度要小：一次提交一个重构手法，方便 review 和回滚
- 重构和新功能开发不要混在同一个提交中
- 大规模重构前先和团队沟通，避免合并冲突
