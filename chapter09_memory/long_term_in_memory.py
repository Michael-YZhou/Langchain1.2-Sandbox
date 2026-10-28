from typing import NotRequired

from langchain.agents import create_agent, AgentState
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import ToolRuntime
from langgraph.store.memory import InMemoryStore

from common.llm import get_chat_model

model = get_chat_model()

store = InMemoryStore()

# 自定义一个继承于AgentState的类，包含user_id
class CustomState(AgentState):
    user_id: NotRequired[str]

@tool(parse_docstring=True)
def save_user_info(name: str, runtime: ToolRuntime) -> str:
    """
    将用户信息保存在长期记忆中

    Args:
        name: 用户名
        runtime: 运行时

    Returns:
        str: 保存状态
    """
    namespace = ("users",)
    key=runtime.state["user_id"]
    value={"name": name}

    runtime.store.put(namespace, key, value)
    return "saved"

@tool(parse_docstring=True)
def get_user_info(runtime: ToolRuntime) -> str:
    """
    从长期记忆中读取用户信息

    Args:
        runtime: 运行时

    Returns:
        str: 用户信息，未找到时返回提示
    """
    namespace = ("users",)
    key = runtime.state["user_id"]

    item = runtime.store.get(namespace, key)
    if item is None:
        return "user info not found"
    return str(item.value)

# noinspection PyTypeChecker
agent = create_agent(
    model=model,
    tools=[save_user_info, get_user_info],
    store=store,
    state_schema=CustomState,
    system_prompt="用户提及个人信息时，使用工具保存用户信息。用户询问个人信息时尝试使用工具读取个人信息"
)
# 第一次对话：告诉agent名字，由save_user_info写入store
response1 = agent.invoke(
    {"messages": [HumanMessage("你好我是Michael")], "user_id": "user_1"}
)

for msg in response1["messages"]:
    msg.pretty_print()

# 第二次对话：没有checkpointer，消息历史不保留，只能通过get_user_info从store读取
response2 = agent.invoke(
    {"messages": [HumanMessage("你好，我是谁？")], "user_id": "user_1"}
)

for msg in response2["messages"]:
    msg.pretty_print()

# 换一个user_id：store中没有这个key，读不到名字
response3 = agent.invoke(
    {"messages": [HumanMessage("你好，我是谁？")], "user_id": "user_2"}
)

for msg in response3["messages"]:
    msg.pretty_print()

print(store.search(("users",)))
