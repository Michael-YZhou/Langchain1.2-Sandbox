from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from common.llm import get_chat_model

model = get_chat_model()

attempts = 0


class WeatherSchema(BaseModel):
    city: str = Field(description="City name to check the weather for")


@tool(description="Check the current weather for a city", args_schema=WeatherSchema)
def check_weather(city: str) -> str:
    global attempts
    attempts += 1
    print(f"check_weather 第 {attempts} 次调用")
    # the fake weather service times out on the first two calls
    if attempts <= 2:
        raise TimeoutError(f"weather service timed out for {city}")
    return f"{city}: sunny, 28°C"


# retry only on TimeoutError: up to 3 retries, waiting 0.5s, 1s, 2s between attempts
agent = create_agent(
    model=model,
    tools=[check_weather],
    middleware=[
        ToolRetryMiddleware(
            max_retries=3, #（最大重试次数，不包括第一次调用）
            retry_on=(TimeoutError,), # 捕获到特定异常时才触发重试
            initial_delay=0.5, # 第一次重试前的初始等待时间（0.5秒）
            max_delay=10, # 最大等待延迟，防止无限延迟
            backoff_factor=2.0, # 指数退避因子（每次重试等待时间乘以2）
            jitter=True, # 开启抖动（等待时间加入随机性）
            on_failure="continue" # 达到最大重试次数后的行为，将错误信息包装后塞回对话历史（不再继续调用工具），让大模型知道失败了并继续
        )
    ]
)

response = agent.invoke({"messages": [HumanMessage("北京今天天气怎么样？")]})

for msg in response["messages"]:
    msg.pretty_print()
