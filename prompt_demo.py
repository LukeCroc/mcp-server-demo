"""
MCP Prompt 功能演示
"""
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

# 创建MCP服务器
mcp = FastMCP("PromptDemo")

# 示例1: 简单的文本prompt
@mcp.prompt(title="代码审查助手")
def code_review(code: str) -> str:
    """请求对给定代码进行审查"""
    return f"请审查以下代码，提供改进建议和安全检查：\n\n```python\n{code}\n```"

# 示例2: 带参数的复杂prompt
@mcp.prompt(title="数据分析报告")
def data_analysis_report(dataset_name: str, analysis_type: str = "summary") -> str:
    """生成数据分析报告模板"""
    templates = {
        "summary": "请为数据集 '{dataset}' 生成一个详细的数据摘要报告",
        "trends": "请分析数据集 '{dataset}' 的趋势和模式",
        "anomalies": "请检测数据集 '{dataset}' 中的异常值"
    }
    return templates.get(analysis_type, templates["summary"]).format(dataset=dataset_name)

# 示例3: 结构化消息序列（高级用法）
@mcp.prompt(title="调试对话")
def debug_conversation(error_message: str) -> list[base.Message]:
    """启动一个调试对话流程"""
    return [
        base.UserMessage("我遇到了一个错误需要帮助调试："),
        base.UserMessage(error_message),
        base.AssistantMessage("我来帮您分析这个问题。请告诉我：\n1. 您尝试过哪些解决方法？\n2. 错误发生时的具体操作步骤？")
    ]

# 示例4: 多语言问候prompt
@mcp.prompt(title="多语言问候生成器")
def multilingual_greeting(name: str, language: str = "english") -> str:
    """生成不同语言的问候语"""
    greetings = {
        "english": f"Hello, {name}! How are you today?",
        "chinese": f"你好，{name}！今天过得怎么样？",
        "spanish": f"¡Hola, {name}! ¿Cómo estás hoy?",
        "french": f"Bonjour, {name}! Comment allez-vous aujourd'hui?"
    }
    return greetings.get(language.lower(), greetings["english"])

# 运行服务器
if __name__ == "__main__":
    mcp.run(transport='stdio')