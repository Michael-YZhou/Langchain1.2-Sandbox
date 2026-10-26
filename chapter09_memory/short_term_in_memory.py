from idlelib import config

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from common.llm import get_chat_model

model = get_chat_model()

agent = create_agent(
    model=model,
    checkpointer=InMemorySaver()
)

config = {"configurable": {"thread_id": "1"}}

response1 = agent.invoke(
    {"messages": [HumanMessage("你好我是Michael")]},
    config=config
)

for msg in response1["messages"]:
    msg.pretty_print()

response2 = agent.invoke(
    {"messages": [HumanMessage("你好，我是谁？")]},
    config=config
)

for msg in response2["messages"]:
    msg.pretty_print()
