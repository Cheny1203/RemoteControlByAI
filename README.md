# AI 地图导航助手

通过语音或文字指令，让AI自动控制浏览器打开地图并设置导航路线。

## 功能特性

- ✅ 支持语音和文字输入
- ✅ 支持百度地图和高德地图
- ✅ 基于 MCP (Model Context Protocol) 实现
- ✅ 使用 Playwright 进行浏览器自动化
- ✅ 集成七牛云 AI 服务进行智能指令解析

## 系统要求

- Python 3.8+
- 麦克风（如需使用语音输入）
- Chrome/Chromium 浏览器

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd python
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 5. 配置 API Key

创建 `.env` 文件并添加你的七牛云 API Key:

```bash
echo "OPENAI_API_KEY=your-qiniu-api-key-here" > .env
```

## 使用方法

### 方式一: 直接运行客户端（推荐）

```bash
python client.py
```

程序会提示你选择输入方式:
- 输入 `text` 使用文字输入
- 输入 `voice` 使用语音输入
- 输入 `quit` 退出程序

### 方式二: 运行 MCP 服务器（高级用法）

如果你想将 MCP 服务器集成到其他应用中:

```bash
python mcp_server.py
```

然后在你的应用中通过 MCP 协议与服务器通信。

## 使用示例

### 文字输入示例

```
请选择输入方式 [text/voice/quit]: text

请输入导航指令 (例如: 从北京到上海): 从天安门到北京西站

选择地图 [baidu/gaode, 默认百度]: baidu
```

### 语音输入示例

```
请选择输入方式 [text/voice/quit]: voice

请说话...
识别到: 从天安门到北京西站

选择地图 [baidu/gaode, 默认百度]: gaode
```

## 项目结构

```
.
├── client.py           # 客户端程序（带语音/文字输入）
├── mcp_server.py       # MCP 服务器（浏览器自动化）
├── requirements.txt    # Python 依赖
├── .env               # 环境变量配置（需自行创建）
├── .gitignore         # Git 忽略文件配置
└── README.md          # 项目文档
```

## 技术架构

### MCP 服务器 (`mcp_server.py`)

提供以下工具:
- `open_browser`: 打开浏览器
- `navigate_baidu_map`: 在百度地图中设置导航
- `navigate_gaode_map`: 在高德地图中设置导航
- `close_browser`: 关闭浏览器

### 客户端 (`client.py`)

- 接受语音或文字输入
- 调用 Claude API 进行指令解析
- 使用 Playwright 执行浏览器操作
- 自动提取起点和终点信息

## 依赖说明

- `mcp`: Model Context Protocol SDK
- `playwright`: 浏览器自动化框架
- `openai`: OpenAI SDK (用于连接七牛云 AI 服务)
- `SpeechRecognition`: 语音识别库
- `PyAudio`: 音频处理库
- `python-dotenv`: 环境变量管理

## 注意事项

1. **API Key**: 需要有效的七牛云 API Key (配置在 OPENAI_API_KEY 环境变量中)
2. **网络连接**: 需要访问七牛云 AI 服务 (https://openai.qiniu.com) 和百度地图/高德地图
3. **语音识别**: 使用 Google 语音识别服务，需要网络连接
4. **浏览器**: 首次运行会自动下载 Chromium 浏览器
5. **AI 模型**: 使用七牛云提供的 deepseek/deepseek-v3.1-terminus 模型

## 故障排除

### 语音识别不工作

确保:
- 麦克风已正确连接
- 系统已授予麦克风访问权限
- 网络连接正常（需访问 Google 服务）

### 浏览器无法打开

运行:
```bash
playwright install chromium
```

### API 调用失败

检查:
- `.env` 文件中的 API Key 是否正确 (七牛云 API Key)
- 网络连接是否正常，能否访问 https://openai.qiniu.com
- API 额度是否充足

## 开发说明

### 扩展其他地图服务

在 `mcp_server.py` 和 `client.py` 中添加新的工具函数:

```python
@self.app.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        # ... 现有工具
        Tool(
            name="navigate_google_map",
            description="在谷歌地图中设置导航",
            inputSchema={...}
        )
    ]
```

### 自定义 AI 行为

修改 `client.py` 中的 `system_prompt` 来改变 AI 的行为模式。

## 许可证

本项目遵循 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！
