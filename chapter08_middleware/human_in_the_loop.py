# Create model object
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from common.llm import get_chat_model

model = get_chat_model()


# Create tools to extend model capability
class WeatherSchema(BaseModel):
    city: str = Field(description="City name to check the weather for")


@tool(description="Get the current weather for a city", args_schema=WeatherSchema)
def get_weather(city: str) -> str:
    return f"{city}: sunny, 28°C"


class StockSchema(BaseModel):
    product: str = Field(default="laptop", description="Product name to look up in the inventory database")


@tool(description="Check the inventory database for a product's stock level", args_schema=StockSchema)
def check_stock(product: str = "laptop") -> str:
    # fake database lookup, no real connection
    return f"{product} stock level: 52"


class MultiplySchema(BaseModel):
    a: int = Field(description="First integer")
    b: int = Field(description="Second integer")


@tool(description="Multiply two integers and return the product", args_schema=MultiplySchema)
def multiply(a: int, b: int) -> int:
    return a * b


tools = [get_weather, check_stock, multiply]


# Create Agent (Model, System prompt, Tools, ToolStrategy, Invoke -> messages array)
class SmartAgent:
    def __init__(self):
        self.model = model
        self.tools = tools
        system_prompt = """
        你是Joi，一个智能助手，你可以帮助用户:
        查询天气用 get_weather 工具
        查询库存用 check_stock 工具
        做乘法运算用 multiply 工具
        """

        # create agent
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=system_prompt,
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on={
                        "get_weather": True,
                        "multiply": True,
                        "check_stock": InterruptOnConfig(
                            allowed_decisions=["approve", "reject"],
                            description="查询库存中断了...",
                        ),
                    },
                    description_prefix="中断啦！"
                ),
            ]
        )

        # chat history
        self.messages = []

    def chat(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})

        result = self.agent.invoke({"messages": self.messages})

        # keep the full conversation (AI replies and tool calls included) for the next turn
        self.messages = result["messages"]

        # the agent returns the whole conversation; the last message is its final AI reply
        last_ai_message = result["messages"][-1]
        print(last_ai_message.content)

    def reset(self):
        self.messages = []


# Main function
def main():
    agent = SmartAgent()

    questions = [
        "杭州今天天气怎么样？",  # get_weather
        "笔记本电脑还有多少库存？",  # check_stock
        "12乘以7等于多少？",  # multiply
        "把刚才的结果再乘以2",  # needs the previous turn from history
    ]
    for question in questions:
        print(f"\nUser: {question}")
        print("Joi: ", end="")
        agent.chat(question)

    # after reset the agent should no longer know the earlier result
    agent.reset()
    print(f"\n(history reset, {len(agent.messages)} messages)")
    print("\nUser: 刚才的乘法结果是多少？")
    print("Joi: ", end="")
    agent.chat("刚才的乘法结果是多少？")


if __name__ == "__main__":
    main()
