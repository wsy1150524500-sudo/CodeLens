# 错误处理最佳实践

## 基本原则

- 不要忽略错误：空的 catch 块是最危险的代码
- 错误应该在能处理它的层级处理，不能处理就向上传播
- 区分可恢复错误（重试、降级）和不可恢复错误（崩溃、告警）
- 错误信息要有用：包含上下文（什么操作、什么输入、什么原因）
- 不要用异常控制正常流程，异常是异常情况

## 异常处理

### 捕获策略
- 捕获具体异常类型，不要 catch Exception/Throwable
- Python: except ValueError 优于 except Exception
- Java: catch (IOException e) 优于 catch (Exception e)
- 多个异常类型可以合并：except (ValueError, TypeError)
- finally/defer 确保资源释放

### 自定义异常
- 业务异常继承自基础业务异常类，和系统异常区分
- 异常类名以 Error 或 Exception 结尾
- 携带错误码和上下文信息
- 分层异常：Controller 层、Service 层、DAO 层各自的异常类型

### 异常转换
- 底层异常不要直接暴露给上层，转换为上层能理解的异常
- 数据库异常 → 业务异常（"用户不存在"而非"SQL error"）
- 保留原始异常作为 cause，方便排查

## Go 风格错误处理

- 返回值携带错误：result, err := doSomething()
- 立即检查错误：if err != nil { return err }
- 错误包装添加上下文：fmt.Errorf("failed to create user: %w", err)
- errors.Is() 和 errors.As() 判断错误类型
- 不要丢弃错误，至少记录日志

## Rust 风格错误处理

- Result<T, E> 类型强制处理错误
- ? 操作符简化错误传播
- 自定义错误类型实现 std::error::Error trait
- thiserror 和 anyhow 库简化错误定义和处理

## 错误日志

- 错误日志包含：时间、请求 ID、用户 ID、操作、输入参数、错误详情、堆栈
- 日志级别：DEBUG < INFO < WARN < ERROR < FATAL
- WARN：可恢复的异常情况（重试成功、降级处理）
- ERROR：需要人工介入的错误（服务不可用、数据不一致）
- 不要在循环中打日志，会产生日志风暴
- 结构化日志（JSON 格式）便于检索和分析

## 重试机制

- 只对临时性错误重试（网络超时、服务暂时不可用）
- 不要对业务错误重试（参数错误、权限不足）
- 指数退避（Exponential Backoff）：1s → 2s → 4s → 8s
- 加随机抖动（Jitter）避免重试风暴
- 设置最大重试次数，避免无限重试
- 幂等性保证：重试不会产生副作用（重复扣款、重复创建）

## 降级与熔断

- 降级：核心功能不可用时提供备选方案（缓存数据、默认值、简化功能）
- 熔断：连续失败超过阈值时快速失败，不再尝试调用（Circuit Breaker 模式）
- 熔断状态：关闭 → 打开 → 半开（尝试恢复）
- 超时设置：每个外部调用都要设超时，不要无限等待
