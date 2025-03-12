python -m app.main
pip install -r requirements.txt

| 阶段 | 时间 | 任务内容 |
|------|------|----------|
| 1 | 0.2 | 项目需求分析与设计|
| 2 | 0.2 | 数据库设计与建模|
| 3 | 第2周 | 用户认证模块开发|
| 4 | 第2周 | 用户管理基础API开发|
| 5 | 第3周 | API安全性增强与权限控制|
| 6 | 第3周 | 单元测试与集成测试|
| 7 | 第4周 | API文档完善|
| 8 | 第4周 | 性能优化与部署准备|
| 9 | 第5周 | 系统部署与环境配置|

### 用户管理

- `GET /users/me` - 获取当前用户信息
- `GET /users/` - 获取所有用户
- `GET /users/{user_id}` - 获取特定用户
- `PUT /users/{user_id}` - 更新用户信息
- `DELETE /users/{user_id}` - 删除用户

### 用户虚拟货币 (Coins)

系统使用整数类型的 coins 作为虚拟货币单位，不支持小数点。这样设计的好处是：

1. 避免浮点数计算中的精度问题
2. 更适合表示不可分割的虚拟货币单位
3. 提高数据库性能

例如，如果您的应用中 1 个真实货币等于 100 coins，那么 10.5 元将表示为 1050 coins。

- `PUT /users/{user_id}/coins` - 设置用户 coins 余额
- `POST /users/{user_id}/coins/add` - 向用户账户添加 coins
- `POST /users/{user_id}/coins/deduct` - 从用户账户扣除 coins
