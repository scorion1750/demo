
访问 <http://localhost:8000/docs> 查看 API 文档。

## API 端点

### 用户认证

- `POST /users/register` - 注册新用户
- `POST /users/token` - 获取访问令牌

### 用户管理

- `GET /users/me` - 获取当前用户信息
- `GET /users/` - 获取所有用户
- `GET /users/{user_id}` - 获取特定用户
- `PUT /users/{user_id}` - 更新用户信息
- `DELETE /users/{user_id}` - 删除用户

## 测试

导入 `postman.json` 到 Postman 中进行 API 测试。

## 常见问题解决

### bcrypt 错误

如果遇到 `AttributeError: module 'bcrypt' has no attribute '__about__'` 错误，请确保安装了兼容版本的 bcrypt：
