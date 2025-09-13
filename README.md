# Claude Code Hooks 配置指南

## 概览

本文档提供了如何配置 Claude Code hooks 来调用通知服务的完整指南。

## Hook 事件类型

Claude Code 支持以下 hook 事件：

1. **tool-call** - 工具调用开始时触发
2. **tool-result** - 工具调用完成时触发  
3. **user-prompt-submit** - 用户提交问题时触发
4. **assistant-response** - 助手响应时触发
5. **conversation-start** - 对话开始时触发
6. **conversation-end** - 对话结束时触发

## 本地 Windows 环境配置

### 1. 启动通知服务

```bash
# 在 Windows 机器上
cd D:\GitHub\ClaudeNote
python main.py
```

服务将在 `http://localhost:8899` 上启动。

### 2. Claude Code Hook 配置

在 Claude Code 配置中添加以下 hooks：

#### 工具相关事件

```bash
# 工具调用开始
claude config hooks add tool-call "curl -X POST http://localhost:8899/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"tool-call\", \"timestamp\": \"$(date -Iseconds)\", \"payload\": {\"tool\": \"$TOOL_NAME\"}}'"

# 工具调用完成
claude config hooks add tool-result "curl -X POST http://localhost:8899/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"tool-result\", \"timestamp\": \"$(date -Iseconds)\", \"payload\": {\"tool\": \"$TOOL_NAME\", \"success\": true}}'"
```

#### 用户交互事件

```bash
# 用户提交问题
claude config hooks add user-prompt-submit "curl -X POST http://localhost:8899/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"user-prompt-submit\", \"timestamp\": \"$(date -Iseconds)\"}'"

# 助手响应
claude config hooks add assistant-response "curl -X POST http://localhost:8899/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"assistant-response\", \"timestamp\": \"$(date -Iseconds)\"}'"
```

#### 对话管理事件

```bash
# 对话开始
claude config hooks add conversation-start "curl -X POST http://localhost:8899/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"conversation-start\", \"timestamp\": \"$(date -Iseconds)\"}'"

# 对话结束
claude config hooks add conversation-end "curl -X POST http://localhost:8899/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"conversation-end\", \"timestamp\": \"$(date -Iseconds)\"}'"
```

## Linux 服务器环境配置

如果 Claude Code 运行在 Linux 服务器上，需要将 `localhost` 替换为 Windows 机器的 IP 地址：

### 1. 获取 Windows 机器 IP

```bash
# 在 Windows 命令行中
ipconfig
```

假设 Windows 机器 IP 为 `192.168.1.100`

### 2. Linux 服务器上的 Hook 配置

```bash
# 设置通知服务器地址
NOTIFICATION_SERVER="http://192.168.1.100:8899"

# 工具调用开始
claude config hooks add tool-call "curl -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"tool-call\", \"timestamp\": \"$(date -Iseconds)\", \"payload\": {\"tool\": \"$TOOL_NAME\"}}'"

# 工具调用完成
claude config hooks add tool-result "curl -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"tool-result\", \"timestamp\": \"$(date -Iseconds)\", \"payload\": {\"tool\": \"$TOOL_NAME\", \"success\": true}}'"

# 用户提交问题
claude config hooks add user-prompt-submit "curl -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"user-prompt-submit\", \"timestamp\": \"$(date -Iseconds)\"}'"

# 助手响应
claude config hooks add assistant-response "curl -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"assistant-response\", \"timestamp\": \"$(date -Iseconds)\"}'"

# 对话开始
claude config hooks add conversation-start "curl -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"conversation-start\", \"timestamp\": \"$(date -Iseconds)\"}'"

# 对话结束  
claude config hooks add conversation-end "curl -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"conversation-end\", \"timestamp\": \"$(date -Iseconds)\"}'"
```

## 高级配置选项

### 1. 一键配置脚本 (Linux/macOS)

```bash
#!/bin/bash
# setup_claude_hooks.sh

# 配置通知服务器地址（修改为实际 IP）
NOTIFICATION_SERVER="http://192.168.1.100:8899"

echo "正在配置 Claude Code hooks..."

# 工具相关事件
claude config hooks add tool-call "curl -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"tool-call\", \"timestamp\": \"$(date -Iseconds)\", \"payload\": {\"tool\": \"$TOOL_NAME\"}}' > /dev/null 2>&1"

claude config hooks add tool-result "curl -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"tool-result\", \"timestamp\": \"$(date -Iseconds)\", \"payload\": {\"tool\": \"$TOOL_NAME\", \"success\": true}}' > /dev/null 2>&1"

# 用户交互事件
claude config hooks add user-prompt-submit "curl -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"user-prompt-submit\", \"timestamp\": \"$(date -Iseconds)\"}' > /dev/null 2>&1"

claude config hooks add assistant-response "curl -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"assistant-response\", \"timestamp\": \"$(date -Iseconds)\"}' > /dev/null 2>&1"

# 对话管理事件
claude config hooks add conversation-start "curl -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"conversation-start\", \"timestamp\": \"$(date -Iseconds)\"}' > /dev/null 2>&1"

claude config hooks add conversation-end "curl -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"conversation-end\", \"timestamp\": \"$(date -Iseconds)\"}' > /dev/null 2>&1"

echo "Claude Code hooks 配置完成！"
echo "通知服务器: $NOTIFICATION_SERVER"
```

### 2. Windows PowerShell 配置脚本

```powershell
# setup_claude_hooks.ps1

# 配置通知服务器地址
$NOTIFICATION_SERVER = "http://localhost:8899"

Write-Host "正在配置 Claude Code hooks..."

# 工具相关事件
claude config hooks add tool-call "curl.exe -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"tool-call\", \"timestamp\": \"$(Get-Date -Format 'o')\", \"payload\": {\"tool\": \"$env:TOOL_NAME\"}}'"

claude config hooks add tool-result "curl.exe -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"tool-result\", \"timestamp\": \"$(Get-Date -Format 'o')\", \"payload\": {\"tool\": \"$env:TOOL_NAME\", \"success\": true}}'"

# 用户交互事件
claude config hooks add user-prompt-submit "curl.exe -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"user-prompt-submit\", \"timestamp\": \"$(Get-Date -Format 'o')\"}'"

claude config hooks add assistant-response "curl.exe -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"assistant-response\", \"timestamp\": \"$(Get-Date -Format 'o')\"}'"

# 对话管理事件
claude config hooks add conversation-start "curl.exe -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"conversation-start\", \"timestamp\": \"$(Get-Date -Format 'o')\"}'"

claude config hooks add conversation-end "curl.exe -s -X POST $NOTIFICATION_SERVER/notify/hook -H 'Content-Type: application/json' -d '{\"event_type\": \"conversation-end\", \"timestamp\": \"$(Get-Date -Format 'o')\"}'"

Write-Host "Claude Code hooks 配置完成！"
Write-Host "通知服务器: $NOTIFICATION_SERVER"
```

## 测试配置

### 1. 测试通知服务

```bash
# 测试服务是否运行
curl http://localhost:8899/health

# 测试音频播放
curl -X POST http://localhost:8899/test/sound/tool_start
curl -X POST http://localhost:8899/test/sound/user_prompt_submit
curl -X POST http://localhost:8899/test/sound/assistant_response
```

### 2. 测试 Hook 事件

```bash
# 手动触发 hook 事件测试
curl -X POST http://localhost:8899/notify/hook \
  -H "Content-Type: application/json" \
  -d '{"event_type": "tool-call", "timestamp": "2024-01-01T12:00:00Z", "payload": {"tool": "test"}}'
```

## 音频文件配置

### 1. 创建音频文件目录

```bash
# 在项目根目录下创建 sounds 目录
mkdir sounds
```

### 2. 添加音频文件

将以下音频文件放入 `sounds/` 目录：

- `tool_start.wav` - 工具开始执行声音
- `tool_complete.wav` - 工具执行完成声音
- `tool_error.wav` - 工具执行错误声音
- `conversation_start.wav` - 对话开始声音
- `conversation_end.wav` - 对话结束声音
- `user_prompt.wav` - 用户提交问题声音
- `assistant_response.wav` - 助手回复声音
- `system_error.wav` - 系统错误声音
- `notification.wav` - 通用通知声音

### 3. 音频文件格式建议

- 格式：WAV 或 MP3
- 时长：1-3 秒
- 音量：适中，不要太响
- 建议使用不同音调区分不同事件类型

## 故障排除

### 1. 运行网络诊断工具（推荐）

```bash
# 运行完整的网络诊断
python network_test.py
```

这个工具会检查：
- 本机IP地址
- 端口是否开放
- HTTP请求是否正常
- 防火墙规则状态
- 诊断建议

### 2. 配置防火墙（解决最常见问题）

**方法一：使用批处理脚本（推荐）**
```cmd
# 以管理员身份运行
setup_firewall.bat
```

**方法二：使用PowerShell脚本**
```powershell
# 以管理员身份运行 PowerShell
.\setup_firewall.ps1
```

**方法三：手动配置**
```cmd
# 以管理员身份运行命令行
netsh advfirewall firewall add rule name="Claude Hook Notification Service" dir=in action=allow protocol=TCP localport=8899
```

### 3. 常见问题排查

#### 问题1: 服务启动但外部无法访问
**症状**：本地 `curl http://localhost:8899/health` 正常，但其他机器无法访问

**解决方案**：
1. 运行防火墙配置脚本：`setup_firewall.bat`
2. 检查Windows Defender防火墙设置
3. 检查第三方防火墙软件（360、McAfee等）

#### 问题2: 端口被占用
**症状**：服务启动失败，提示端口被占用

**解决方案**：
```cmd
# 查看端口占用
netstat -ano | findstr :8899

# 终止占用进程（替换PID为实际进程ID）
taskkill /PID <进程ID> /F

# 或修改配置使用其他端口
```

#### 问题3: uvicorn 启动问题
**症状**：服务启动时出现模块导入错误

**已修复**：将 `uvicorn.run("main:app")` 改为 `uvicorn.run(app)`，直接传递应用对象

### 4. 手动测试命令

```bash
# 检查服务状态
curl http://localhost:8899/health

# 检查音频配置
curl http://localhost:8899/sounds/list

# 测试音频播放
curl -X POST http://localhost:8899/test/sound/tool_start
```

### 5. 检查 Hook 配置

```bash
# 查看当前配置的 hooks
claude config hooks list

# 删除特定 hook
claude config hooks remove tool-call

# 删除所有 hooks
claude config hooks clear
```

### 6. 获取本机IP地址

**Windows：**
```cmd
ipconfig
```

**PowerShell：**
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne "127.0.0.1"}
```

## 网络配置注意事项

### Windows 防火墙配置
1. **自动配置**：运行 `setup_firewall.bat` 或 `setup_firewall.ps1`
2. **手动配置**：
   - 打开 Windows Defender 防火墙
   - 选择"允许应用或功能通过防火墙"
   - 添加端口 8899 的入站规则

### 网络环境检查
1. **局域网访问**：确保设备在同一网段
2. **网络发现**：启用网络发现和文件共享
3. **代理设置**：如使用代理，在 curl 命令中添加 `--proxy` 参数
4. **路由器设置**：检查路由器是否有端口过滤

### 第三方防火墙
常见软件可能阻止连接：
- 360 安全卫士
- McAfee
- Norton
- Kaspersky

需要在这些软件中添加端口例外。

## 服务管理

### 1. 后台运行服务

#### Windows
```cmd
# 使用 Python 后台运行
start /B python main.py

# 或使用 PowerShell
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
```

#### Linux/macOS
```bash
# 使用 nohup 后台运行
nohup python main.py &

# 或使用 systemd service (推荐)
# 创建 /etc/systemd/system/claude-notify.service
```

### 2. 开机自启动

#### Windows
- 将脚本添加到启动文件夹
- 或使用任务计划程序

#### Linux
- 创建 systemd service
- 或添加到 crontab @reboot

这样配置完成后，当 Claude Code 执行各种操作时，就会自动调用通知服务播放相应的声音提醒。