from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from common.llm import get_chat_model

model = get_chat_model()


class WeatherSchema(BaseModel):
    city: str = Field(description="City name to check the weather for")


@tool(description="Get the current weather for a city", args_schema=WeatherSchema)
def get_weather(city: str) -> str:
    return f"{city}: sunny, 28°C"


class MultiplySchema(BaseModel):
    a: int = Field(description="First integer")
    b: int = Field(description="Second integer")


@tool(description="Multiply two integers and return the product", args_schema=MultiplySchema)
def multiply(a: int, b: int) -> int:
    return a * b


class StockSchema(BaseModel):
    product: str = Field(description="Product name to look up in the inventory database")


@tool(description="Check the inventory database for a product's stock level", args_schema=StockSchema)
def check_stock(product: str) -> str:
    # fake database lookup, no real connection
    return f"{product} stock level: 52"


# TodoListMiddleware adds a write_todos tool and keeps the list in state["todos"]
agent = create_agent(
    model=model,
    tools=[get_weather, multiply, check_stock],
    system_prompt="""
    你是一个智能助手。遇到多步骤任务时，先用 write_todos 工具列出待办列表，
    然后逐项执行，每完成一项就立即调用 write_todos 把它标记为 completed，
    全部完成后再给出最终回答。
    """,
    middleware=[TodoListMiddleware()]
)

response = agent.invoke(
    {
        "messages": [
            HumanMessage("帮我做三件事：查一下北京的天气；查一下 laptop 的库存；再把库存数量乘以 3")
        ]
    }
)

for msg in response["messages"]:
    msg.pretty_print()

print("\n最终待办列表:")
for todo in response["todos"]:
    print(f"[{todo['status']}] {todo['content']}")
