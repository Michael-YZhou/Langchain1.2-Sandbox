from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware
from langchain_core.messages import HumanMessage

from common.llm import get_chat_model

# a model name the API doesn't know, so every call fails and the middleware keeps retrying
model = get_chat_model().model_copy(update={"model_name": "no-such-model"})

attempts = 0


def should_retry(e: Exception) -> bool:
    # called after each failed call: print the error, then retry on anything
    global attempts
    attempts += 1
    print(f"模型第 {attempts} 次调用失败: {type(e).__name__}")
    return True


agent = create_agent(
    model=model,
    middleware=[
        ModelRetryMiddleware(
            max_retries=2,  # 最大重试次数，不包括第一次调用
            retry_on=should_retry,  # 返回 True 时才重试
            initial_delay=0.5,  # 第一次重试前等待 0.5 秒，之后每次乘以 backoff_factor
            backoff_factor=2.0,
            on_failure="continue"  # 重试用完后返回一条带错误信息的 AIMessage，而不是抛出异常
        )
    ]
)

response = agent.invoke({"messages": [HumanMessage("用一句话介绍你自己")]})

for msg in response["messages"]:
    msg.pretty_print()
