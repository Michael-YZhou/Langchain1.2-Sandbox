from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import FilesystemFileSearchMiddleware
from langchain_core.messages import HumanMessage

from common.llm import get_chat_model

model = get_chat_model()

# repo root, resolved from this file so the search doesn't depend on the working directory
repo_root = Path(__file__).resolve().parent.parent

agent = create_agent(
    model=model,
    tools=[], #中间件会自动添加 Glob 和 Grep 工具
    middleware=[
        FilesystemFileSearchMiddleware(
            root_path=str(repo_root), # 搜索目录
            use_ripgrep=False,
            max_file_size_mb=10 # 单次读取文件至内存的最大size(mb)
        ),
    ]
)

response = agent.invoke({
    "messages": [HumanMessage("找到定义了multiply函数的Python文件")]
})

for msg in response["messages"]:
    msg.pretty_print()
