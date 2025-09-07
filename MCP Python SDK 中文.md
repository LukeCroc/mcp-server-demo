MCP Python SDK 简明中文指导文档
概述
MCP (Model Context Protocol) Python SDK 是一个用于构建和连接 MCP 服务器的 Python 实现。MCP 协议允许应用程序以标准化方式为 LLM 提供上下文，将提供上下文与实际 LLM 交互的关注点分离。

核心功能
构建 MCP 客户端：连接任何 MCP 服务器
创建 MCP 服务器：暴露资源、提示和工具
支持标准传输：stdio、SSE 和 Streamable HTTP
处理所有 MCP 协议消息和生命周期事件
安装
使用 uv（推荐）
uv init mcp-server-demo
cd mcp-server-demo
uv add "mcp[cli]"

bash


使用 pip
pip install "mcp[cli]"

bash


快速开始
创建简单服务器
from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器
mcp = FastMCP("Demo")

# 添加工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# 添加资源
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# 添加提示
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    return f"Please write a {style} greeting for someone named {name}."

python


运行服务器
# 开发模式测试
uv run mcp dev server.py

# 安装到 Claude Desktop
uv run mcp install server.py

bash


核心概念
1. 服务器 (Server)
MCP 服务器的核心接口，处理连接管理、协议合规性和消息路由。

2. 资源 (Resources)
类似 REST API 的 GET 端点，提供数据但不执行计算或有副作用。

@mcp.resource("file://documents/{name}")
def read_document(name: str) -> str:
    return f"Content of {name}"

python


3. 工具 (Tools)
允许 LLM 通过服务器执行操作，可以执行计算和有副作用。

@mcp.tool()
def sum(a: int, b: int) -> int:
    return a + b

python


4. 提示 (Prompts)
可重用的模板，帮助 LLM 与服务器有效交互。

@mcp.prompt(title="Code Review")
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

python


5. 上下文 (Context)
自动注入到工具和资源函数中，提供 MCP 功能访问。

@mcp.tool()
async def my_tool(x: int, ctx: Context) -> str:
    await ctx.info("Processing...")
    return f"Result: {x}"

python


高级功能
结构化输出
工具可以返回结构化数据，支持 Pydantic 模型、TypedDicts、数据类等。

class WeatherData(BaseModel):
    temperature: float
    condition: str

@mcp.tool()
def get_weather(city: str) -> WeatherData:
    return WeatherData(temperature=22.5, condition="sunny")

python


生命周期管理
使用 lifespan 管理服务器启动和关闭时的资源初始化。

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    db = await Database.connect()
    try:
        yield {"db": db}
    finally:
        await db.disconnect()

python


认证支持
支持 OAuth 2.1 资源服务器功能，用于访问受保护的资源。

运行方式
1. 开发模式
uv run mcp dev server.py

bash


2. Streamable HTTP 传输（生产推荐）
mcp.run(transport="streamable-http")

python


3. 集成到现有 ASGI 服务器
app = Starlette(routes=[Mount("/mcp", app=mcp.streamable_http_app())])

python


客户端开发
连接服务器
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()

python


最佳实践
使用 FastMCP 简化开发过程
利用结构化输出 提供类型安全的数据
实现适当的错误处理 和日志记录
使用 lifespan 管理 共享资源
考虑认证需求 保护敏感操作
资源
官方文档
规范说明
示例代码
这个 SDK 提供了构建强大 MCP 服务器所需的所有工具，使得 LLM 应用程序能够安全、标准化地访问外部数据和功能。