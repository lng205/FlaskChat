# Dev Log

![task](task.jpg)

In this project, we are exchanging the public key via the server, a practice that potentially exposes the system to man-in-the-middle attacks, rendering it inherently insecure.

To resolve this issue, we can sign the client's public key by a verified CA, or we can exchange the key via an existing secure protocol(e.g. In person). However, such measures fall outside the purview of this project's scope.

The remaining part of the project seems secure logically, and satisfies the requirements.  Only the two communicating parties have the capability to decipher the message, and ensure that the message is not tampered with secretly.

Currnet Bugs:

1. History's order may change
2. Scenarios where there are multiple users in the same room not tested

## Designs

### Token

The purpose of the token is to verify that the current user is indeed the individual who initially logged in, ensuring that the server processes requests solely from authenticated users.

We utilize PyJWT to create the token, incorporating the user's username and an expiration time. Upon login, this token is saved in the client's cookie and accompanies each request sent to the server.

Although the requirements mandate authentication for all requests, we selectively authenticate only those involving user-specific actions. Requests for public keys or encrypted history are not authenticated. Since all messages in the chat room are encrypted, the server is unaware of their content and does not require user identification for message transmission.

However, should the need arise to authenticate additional requests, we can effortlessly integrate the authentication code into the relevant view function.

## Timeline

### 4/1

- 15:00 - 18:00: 理解项目需求，配置开发环境，熟悉代码框架
- 20:00 - 20:40: 会议分享讲解代码框架的实现逻辑，讨论好友功能的实现方式，讨论数据库设计
- 20:40 - 23:00: 开发好友功能

### 4/2

- 8:30 - 10:30: 使用SqlAlchemy设计数据库，建立多对多自引用关系，调整前端设计，实现好友功能。具体包括：
  - 好友请求的发送和接收
  - 好友请求的接受
  - 好友列表的显示
- 20:00 - 21:00: 会议分享讲解好友功能的实现逻辑，讨论消息加密的实现方式，完善好友功能：拒绝请求；聊天时检查好友关系

### 4/3

- 10:30 - 12:30: 整理会议中的代码改动，优化代码细节，构思消息加密策略
- 15:00 - 18:00: 查阅信息安全资料，设计消息加密方案，文字讨论加密策略
- 19:00 - 22:00: 实现在用户本地生成对称密钥，并通过JS localStorage存储私钥，通过服务器存储公钥。重新理解题目要求，优化消息加密方案

### 4/4

- 9:00 - 12:00: 实现加密消息
- 15:00 - 18:00: 实现解密接收，实现加密消息记录，实现HTTPS，实现token验证

### 4/5

- 9:00 - 12:00: 修复bug，测试
- 15:00 - 18:00: 重构异步JS代码，修复首次发送消息失败的bug